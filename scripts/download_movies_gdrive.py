import zipfile
from pathlib import Path
import shutil
import gdown

# Google Drive file ID của Top 10000 Movies dataset
DRIVE_FILE_ID = '1clZ8WE1p3wxiJblDGf-0EAxHa33Bp61m'
DRIVE_URL = f'https://drive.google.com/uc?id={DRIVE_FILE_ID}'

ZIP_FILE = 'dataset.zip'
EXTRACT_DIR = 'dataset'
TARGET_CSV = Path('data/raw/movies.csv')


def download_from_gdrive():
    print(f'Downloading from Google Drive...')
    gdown.download(DRIVE_URL, ZIP_FILE, quiet=False)
    print(f'Downloaded {ZIP_FILE}')


def extract_zip():
    print(f'Extracting {ZIP_FILE}...')
    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)
    print(f'Extracted to {EXTRACT_DIR}/')


def find_and_move_csv():
    extract_path = Path(EXTRACT_DIR)
    csv_files = list(extract_path.rglob('*.csv'))
    
    if not csv_files:
        raise FileNotFoundError(f'No CSV file found in {EXTRACT_DIR}/')
    
    # Lấy CSV đầu tiên tìm thấy
    source_csv = csv_files[0]
    print(f'Found CSV: {source_csv}')
    
    # Tạo thư mục đích
    TARGET_CSV.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy CSV
    shutil.copy(source_csv, TARGET_CSV)
    print(f'Copied to {TARGET_CSV}')


def cleanup():
    print('Cleaning up temporary files...')
    if Path(ZIP_FILE).exists():
        Path(ZIP_FILE).unlink()
    if Path(EXTRACT_DIR).exists():
        shutil.rmtree(EXTRACT_DIR)
    print('Cleanup complete!')


def main():
    try:
        download_from_gdrive()
        extract_zip()
        find_and_move_csv()
        cleanup()
        print(f'\n✅ Dataset ready at {TARGET_CSV}')
        print('Now you can run: python server.py')
    except Exception as e:
        print(f'❌ Error: {e}')
        raise


if __name__ == '__main__':
    main()
