import requests
import json
import os
from tqdm import tqdm
import time
from datetime import datetime, timedelta

# Cấu hình API
API_KEY = "80673fb813648fa120c56b13129ea192"
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"
TMDB_VIDEO_BASE_URL = "https://www.themoviedb.org/movie/"

# Tạo thư mục để lưu dữ liệu
def create_directories():
    if not os.path.exists('data'):
        os.makedirs('data')

# Lấy thông tin chi tiết của phim
def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "language": "vi-VN",
        "append_to_response": "videos"
    }
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

# Lấy danh sách phim phổ biến
def get_popular_movies(page):
    url = f"{BASE_URL}/movie/popular"
    params = {
        "api_key": API_KEY,
        "language": "vi-VN",
        "page": page
    }
    response = requests.get(url, params=params)
    return response.json()['results'] if response.status_code == 200 else []

# Lấy danh sách phim sắp chiếu
def get_upcoming_movies(page):
    url = f"{BASE_URL}/movie/upcoming"
    params = {
        "api_key": API_KEY,
        "language": "vi-VN",
        "page": page
    }
    response = requests.get(url, params=params)
    return response.json()['results'] if response.status_code == 200 else []

# Lấy danh sách phim đang chiếu
def get_now_playing_movies(page):
    url = f"{BASE_URL}/movie/now_playing"
    params = {
        "api_key": API_KEY,
        "language": "vi-VN",
        "page": page
    }
    response = requests.get(url, params=params)
    return response.json()['results'] if response.status_code == 200 else []

def process_movie(movie_details):
    if movie_details:
        # Tạo cấu trúc dữ liệu cho Firebase
        processed_movie = {
            "id": movie_details.get('id'),
            "title": movie_details.get('title'),
            "original_title": movie_details.get('original_title'),
            "overview": movie_details.get('overview'),
            "release_date": movie_details.get('release_date'),
            "vote_average": movie_details.get('vote_average'),
            "vote_count": movie_details.get('vote_count'),
            "popularity": movie_details.get('popularity'),
            "runtime": movie_details.get('runtime'),
            "status": movie_details.get('status'),
            "genres": [{"id": genre['id'], "name": genre['name']} for genre in movie_details.get('genres', [])],
            "images": {
                "poster": f"{IMAGE_BASE_URL}{movie_details['poster_path']}" if movie_details.get('poster_path') else None,
                "backdrop": f"{IMAGE_BASE_URL}{movie_details['backdrop_path']}" if movie_details.get('backdrop_path') else None
            },
            "videos": {
                "trailer": f"{TMDB_VIDEO_BASE_URL}{movie_details['id']}/videos" if movie_details.get('videos', {}).get('results') else None
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return processed_movie
    return None

def main():
    create_directories()
    movies_data = {
        "popular": [],
        "coming_soon": [],
        "now_showing": []
    }
    
    # Lấy 10 phim phổ biến
    print("Đang tải phim phổ biến...")
    with tqdm(total=10, desc="Phim phổ biến") as pbar:
        page = 1
        while len(movies_data["popular"]) < 10:
            movies = get_popular_movies(page)
            if not movies:
                break
                
            for movie in movies:
                if len(movies_data["popular"]) >= 10:
                    break
                    
                movie_id = movie['id']
                movie_details = get_movie_details(movie_id)
                processed_movie = process_movie(movie_details)
                
                if processed_movie:
                    movies_data["popular"].append(processed_movie)
                    pbar.update(1)
                
                time.sleep(0.5)
            page += 1

    # Lấy 10 phim sắp chiếu
    print("\nĐang tải phim sắp chiếu...")
    with tqdm(total=10, desc="Phim sắp chiếu") as pbar:
        page = 1
        while len(movies_data["coming_soon"]) < 10:
            movies = get_upcoming_movies(page)
            if not movies:
                break
                
            for movie in movies:
                if len(movies_data["coming_soon"]) >= 10:
                    break
                    
                movie_id = movie['id']
                movie_details = get_movie_details(movie_id)
                processed_movie = process_movie(movie_details)
                
                if processed_movie:
                    movies_data["coming_soon"].append(processed_movie)
                    pbar.update(1)
                
                time.sleep(0.5)
            page += 1

    # Lấy 10 phim đang chiếu
    print("\nĐang tải phim đang chiếu...")
    with tqdm(total=10, desc="Phim đang chiếu") as pbar:
        page = 1
        while len(movies_data["now_showing"]) < 10:
            movies = get_now_playing_movies(page)
            if not movies:
                break
                
            for movie in movies:
                if len(movies_data["now_showing"]) >= 10:
                    break
                    
                movie_id = movie['id']
                movie_details = get_movie_details(movie_id)
                processed_movie = process_movie(movie_details)
                
                if processed_movie:
                    movies_data["now_showing"].append(processed_movie)
                    pbar.update(1)
                
                time.sleep(0.5)
            page += 1

    # Lưu dữ liệu phim vào file JSON
    with open('data/movie_data.json', 'w', encoding='utf-8') as f:
        json.dump(movies_data, f, ensure_ascii=False, indent=2)

    print(f"\nĐã tải xong:")
    print(f"- {len(movies_data['popular'])} phim phổ biến")
    print(f"- {len(movies_data['coming_soon'])} phim sắp chiếu")
    print(f"- {len(movies_data['now_showing'])} phim đang chiếu")
    print("Dữ liệu đã được lưu vào file 'data/movie_data.json'")

if __name__ == "__main__":
    main()
