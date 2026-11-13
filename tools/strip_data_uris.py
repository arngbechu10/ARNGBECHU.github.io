"""index.html 안의 긴 base64(이미지·소리)를 DATAURI로 바꾼 '읽기 전용' 사본을 만듭니다.
줄 번호는 원본과 같아서, 코드를 읽고 위치를 찾을 때 쓰면 편해요. 수정은 원본 index.html에 하세요.
사용: python3 tools/strip_data_uris.py  →  index.readable.html 생성"""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
h = (root / 'index.html').read_text(encoding='utf-8')
s = re.sub(r'data:[a-z]+/[a-z0-9+.-]+;base64,[A-Za-z0-9+/=]{200,}', 'DATAURI', h)
(root / 'index.readable.html').write_text(s, encoding='utf-8')
print('index.readable.html', len(s.splitlines()), 'lines')
