# PageIndex API

Chatbot에서 사용하는 PageIndex API 명세입니다.

- **Base URL**: `http://localhost:8002` (Playground 백엔드는 `/api/v1/pageindex/*` 로 프록시)
- **엔드포인트**: `GET /health`, `POST /documents`, `GET /jobs/{job_id}`, `GET /documents`, `GET /documents/{document_id}/toc`, `POST /documents/{document_id}/query`, `DELETE /documents/{document_id}`

상세 요청/응답 형식은 PageIndex 프로젝트의 API 문서를 참고하세요.
