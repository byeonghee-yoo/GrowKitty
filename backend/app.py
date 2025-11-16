from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import yaml
import subprocess
import os
app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "파이썬 서버 잘 돌아간다!"

@app.post("/save")
def save():
    data = request.get_json()
    print("data: ", data)
    with open("data.json", "w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)
    return "저장됨"

@app.get("/load")
def load():
    try:
        with open("data.txt", "r", encoding="utf-8") as f:
            data = f.read()
        return jsonify({"data": data})
    except FileNotFoundError:
        return jsonify({"error": "파일을 찾을 수 없습니다."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/update")
def update_yaml():
    try:
        print("POST /update 요청 받음")
        body = request.get_json()
        print(f"요청 본문: {body}")

        yml_path = r"C:\Users\casey\myblog\_config.yml"
        
        # 파일 존재 여부 확인
        if not os.path.exists(yml_path):
            print(f"파일을 찾을 수 없음: {yml_path}")
            return jsonify({"error": f"파일을 찾을 수 없습니다: {yml_path}"}), 404

        print(f"파일 읽기 시작: {yml_path}")
        # YAML 읽기
        with open(yml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # 수정
        if body:
            data["title"] = body.get("title", data["title"])
            print(f"제목 업데이트: {data['title']}")

        # 다시 쓰기
        print("파일 쓰기 시작")
        with open(yml_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)

        # Jekyll 빌드 재실행
        blog_dir = r"C:\Users\casey\myblog"
        if not os.path.exists(blog_dir):
            print(f"블로그 디렉토리를 찾을 수 없음: {blog_dir}")
            return jsonify({"error": f"블로그 디렉토리를 찾을 수 없습니다: {blog_dir}"}), 404
        
        print("Jekyll 빌드 시작")
        # bundle exec jekyll build 실행
        # Windows에서 bundle 명령어를 찾기 위해 shell=True 사용
        # shell=True를 사용하면 Windows에서 PATH 환경 변수를 통해 bundle을 찾을 수 있음
        result = subprocess.run(
            "bundle exec jekyll build",
            cwd=blog_dir,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        
        if result.returncode != 0:
            print(f"Jekyll 빌드 실패: {result.stderr}")
            return jsonify({
                "error": "Jekyll 빌드 실패",
                "stderr": result.stderr,
                "stdout": result.stdout
            }), 500

        print("성공적으로 완료")
        return jsonify({"status": "ok", "updated": data, "build_output": result.stdout})
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {str(e)}")
        return jsonify({"error": f"파일을 찾을 수 없습니다: {str(e)}"}), 404
    except Exception as e:
        print(f"예외 발생: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    print(f"404 오류 발생: {request.method} {request.path}")
    print(f"등록된 라우트: {[str(rule) for rule in app.url_map.iter_rules()]}")
    return jsonify({"error": f"라우트를 찾을 수 없습니다: {request.method} {request.path}"}), 404

app.run(debug=True)