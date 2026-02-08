import sys
import os
import gzip
import json
import subprocess

# --- FINAL SCHEMA (Targeting Field 501) ---
PROTO_CONTENT = """
syntax = "proto3";

message Backup {
  // Standard Manga Fields
  repeated BackupManga backupManga = 1;
  repeated BackupCategory backupCategories = 2;

  // ANIME IS HERE (Field 501)
  repeated BackupAnime backupAnime = 501;
  repeated BackupCategory backupAnimeCategories = 105; 
}

message BackupManga {
  int64 source = 1;
  string url = 2;
  string title = 3;
  string artist = 4;
  string author = 5;
  string description = 6;
  repeated string genre = 7;
  int32 status = 8;
  string thumbnailUrl = 9;
  int64 dateAdded = 13;
  int32 viewer = 14;
  int32 chapters = 16; 
  repeated BackupTracking backupTracking = 15;
  repeated BackupHistory backupHistory = 17;
}

message BackupAnime {
  // We assume the internal structure is standard, just the container ID moved.
  int64 source = 1;
  string url = 2;
  string title = 3;
  string artist = 4;
  string author = 5;
  string description = 6;
  repeated string genre = 7;
  int32 status = 8;
  string thumbnailUrl = 9;
  int64 dateAdded = 13;
  int32 viewer = 14;
  
  // Episodes are field 16 in standard Aniyomi
  int32 episodes = 16; 
  
  repeated BackupTracking backupTracking = 15;
  repeated BackupHistory backupHistory = 17;
}

message BackupTracking {
  int32 syncId = 1;
  int64 libraryId = 2;
  int32 mediaId = 3;
  string trackingUrl = 4;
  string title = 5;
  float lastChapterRead = 6;
  int32 totalChapters = 7;
  float score = 8;
  int32 status = 9;
  int64 startedReadingDate = 10;
  int64 finishedReadingDate = 11;
}

message BackupHistory {
  string url = 1;
  int64 lastRead = 2;
  int64 readDuration = 3;
}

message BackupCategory {
  string name = 1;
  int32 order = 2;
  int32 flags = 3;
}
"""

def main():
    input_file = "latest-backup.tachibk"
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    output_file = input_file + ".json"

    print("📝 Writing 501-target schema...")
    with open("schema.proto", "w") as f:
        f.write(PROTO_CONTENT)

    print("🔨 Compiling schema...")
    try:
        subprocess.run(["protoc", "--python_out=.", "schema.proto"], check=True)
    except Exception:
        print("❌ Error: 'protoc' failed.")
        return

    try:
        import schema_pb2
        from google.protobuf.json_format import MessageToDict
        import importlib
        importlib.reload(schema_pb2)
    except ImportError as e:
        print(f"❌ Error importing schema: {e}")
        return

    print(f"📂 Reading: {input_file}")
    if not os.path.exists(input_file):
        print("❌ File not found.")
        return

    try:
        with gzip.open(input_file, 'rb') as f:
            data = f.read()

        backup = schema_pb2.Backup() #type: ignore
        backup.ParseFromString(data)

        print("🔄 Converting to JSON...")
        result = MessageToDict(backup, preserving_proto_field_name=True)

        # Basic cleanup for output
        if 'backupAnime' not in result:
             result['backupAnime'] = []

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

        print(f"✨ SUCCESS! Saved to: {output_file}")
        print(f"📊 Stats: {len(result.get('backupManga', []))} Manga, {len(result.get('backupAnime', []))} Anime.")

    except Exception as e:
        print(f"❌ Error: {e}")

    print("cleaning protocbuf files")
    os.remove("./schema.proto")
    os.remove("./schema_pb2.py")
    print("completed")

if __name__ == "__main__":
    main()

