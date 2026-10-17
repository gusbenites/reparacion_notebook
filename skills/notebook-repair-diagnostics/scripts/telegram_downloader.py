"""
Telegram Schemas & BIOS Downloader
===================================
Script para buscar y descargar esquemáticos, boardviews y BIOS desde canales de Telegram.

Uso:
    python telegram_downloader.py search "LA-B801P" --channel schematicslaptop
    python telegram_downloader.py download <message_id> --channel schematicslaptop
    python telegram_downloader.py index --channel schematicslaptop
    python telegram_downloader.py recent --channel biosarchive --limit 50

Requisitos:
    pip install telethon

Configuración:
    Crear un archivo telegram_config.json con:
    {
        "api_id": 123456,
        "api_hash": "tu_api_hash_aqui",
        "phone": "+5491123456789"
    }
"""

import asyncio
import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

try:
    from telethon import TelegramClient
    from telethon.tl.types import MessageMediaDocument
except ImportError:
    print("Error: telethon no instalado. Ejecuta: pip install telethon")
    sys.exit(1)


# Configuración
CONFIG_FILE = "telegram_config.json"
DOWNLOAD_DIR = Path("downloads")
INDEX_FILE = Path("telegram_index.json")

# Canales conocidos
CHANNELS = {
    "schematics": "schematicslaptop",
    "bios": "biosarchive",
}


def load_config():
    """Cargar configuración de Telegram desde archivo JSON."""
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: No se encontró {CONFIG_FILE}")
        print("\nCrea un archivo telegram_config.json con:")
        print(json.dumps({
            "api_id": 123456,
            "api_hash": "tu_api_hash_aqui",
            "phone": "+5491123456789"
        }, indent=2))
        print("\nObtén tu API ID y Hash en: https://my.telegram.org")
        sys.exit(1)

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def get_channel_entity(channel_name):
    """Obtener el nombre del canal desde el alias o usar el nombre directamente."""
    return CHANNELS.get(channel_name, channel_name)


async def search_messages(client, channel, query, limit=50):
    """Buscar mensajes con archivos que coincidan con la query."""
    channel_entity = get_channel_entity(channel)
    results = []

    print(f"Buscando '{query}' en @{channel_entity}...")

    async for message in client.iter_messages(channel_entity, limit=limit):
        if message.text and query.lower() in message.text.lower():
            file_info = None
            if message.media and isinstance(message.media, MessageMediaDocument):
                doc = message.media.document
                file_name = None
                file_size = doc.size if hasattr(doc, 'size') else 0

                # Extraer nombre del archivo
                for attr in doc.attributes:
                    if hasattr(attr, 'file_name'):
                        file_name = attr.file_name
                        break

                file_info = {
                    "file_name": file_name or f"file_{message.id}",
                    "file_size": file_size,
                    "mime_type": doc.mime_type if hasattr(doc, 'mime_type') else "unknown",
                }

            results.append({
                "message_id": message.id,
                "date": message.date.isoformat() if message.date else None,
                "text": message.text[:500] if message.text else None,
                "file": file_info,
            })

    return results


async def download_file(client, channel, message_id, output_dir=None):
    """Descargar un archivo específico por su message_id."""
    channel_entity = get_channel_entity(channel)

    if output_dir is None:
        output_dir = DOWNLOAD_DIR / channel
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Descargando mensaje {message_id} de @{channel_entity}...")

    message = await client.get_messages(channel_entity, ids=message_id)

    if not message or not message.media:
        print("Error: El mensaje no contiene archivos.")
        return None

    file_path = await client.download_media(message.media, file=str(output_dir))

    if file_path:
        print(f"Archivo descargado: {file_path}")
        return file_path
    else:
        print("Error al descargar el archivo.")
        return None


async def build_index(client, channel, limit=500):
    """Construir un índice JSON de todos los archivos del canal."""
    channel_entity = get_channel_entity(channel)
    index = {
        "channel": channel_entity,
        "last_update": datetime.now().isoformat(),
        "files": []
    }

    print(f"Construyendo índice de @{channel_entity} (últimos {limit} mensajes)...")

    async for message in client.iter_messages(channel_entity, limit=limit):
        if message.media and isinstance(message.media, MessageMediaDocument):
            doc = message.media.document
            file_name = None
            file_size = doc.size if hasattr(doc, 'size') else 0

            for attr in doc.attributes:
                if hasattr(attr, 'file_name'):
                    file_name = attr.file_name
                    break

            index["files"].append({
                "message_id": message.id,
                "date": message.date.isoformat() if message.date else None,
                "file_name": file_name or f"file_{message.id}",
                "file_size": file_size,
                "mime_type": doc.mime_type if hasattr(doc, 'mime_type') else "unknown",
                "text_preview": message.text[:200] if message.text else None,
            })

    # Guardar índice
    index_path = INDEX_FILE.with_name(f"telegram_index_{channel}.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"Índice guardado: {index_path}")
    print(f"Total de archivos indexados: {len(index['files'])}")

    return index


async def list_recent(client, channel, limit=50):
    """Listar los últimos archivos del canal."""
    channel_entity = get_channel_entity(channel)
    files = []

    print(f"Últimos {limit} archivos de @{channel_entity}:")
    print("-" * 80)

    async for message in client.iter_messages(channel_entity, limit=limit):
        if message.media and isinstance(message.media, MessageMediaDocument):
            doc = message.media.document
            file_name = None

            for attr in doc.attributes:
                if hasattr(attr, 'file_name'):
                    file_name = attr.file_name
                    break

            file_name = file_name or f"file_{message.id}"
            date_str = message.date.strftime("%Y-%m-%d") if message.date else "N/A"

            files.append({
                "message_id": message.id,
                "date": date_str,
                "file_name": file_name,
            })

            print(f"[{date_str}] {file_name} (ID: {message.id})")

    return files


async def main():
    parser = argparse.ArgumentParser(
        description="Descargador de esquemáticos y BIOS desde canales de Telegram"
    )
    parser.add_argument(
        "action",
        choices=["search", "download", "index", "recent"],
        help="Acción a realizar"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Término de búsqueda (para 'search') o message_id (para 'download')"
    )
    parser.add_argument(
        "--channel",
        default="schematics",
        choices=list(CHANNELS.keys()) + list(CHANNELS.values()),
        help="Canal de Telegram (default: schematics)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Límite de mensajes a buscar"
    )
    parser.add_argument(
        "--output",
        help="Carpeta de descarga (para 'download')"
    )

    args = parser.parse_args()

    if args.action in ["search", "download"] and not args.query:
        parser.error(f"'{args.action}' requiere una query o message_id")

    config = load_config()

    async with TelegramClient(
        "telegram_session",
        config["api_id"],
        config["api_hash"]
    ) as client:

        if not await client.is_user_authorized():
            print("Primera vez: se enviará un código de verificación a tu Telegram.")
            await client.send_code_request(config["phone"])
            code = input("Ingresa el código recibido: ")
            await client.sign_in(config["phone"], code)

        if args.action == "search":
            results = await search_messages(client, args.channel, args.query, args.limit)
            print(f"\nSe encontraron {len(results)} resultados:")
            print(json.dumps(results, ensure_ascii=False, indent=2))

        elif args.action == "download":
            message_id = int(args.query)
            await download_file(client, args.channel, message_id, args.output)

        elif args.action == "index":
            await build_index(client, args.channel, args.limit)

        elif args.action == "recent":
            await list_recent(client, args.channel, args.limit)


if __name__ == "__main__":
    asyncio.run(main())
