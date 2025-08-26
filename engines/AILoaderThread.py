import os
import time
from PySide6.QtCore import QThread, Signal

# AI 엔진 임포트
from core.llm_factory import get_chat_controller
from engines.q_stable_engine import QStableV21Engine
from engines.img_to_text_engine import DummyImgToTextEngine

class AILoaderThread(QThread):
    progress_updated = Signal(str)  # 로딩 진행상황
    model_loaded = Signal(str, object)  # 모델명, 모델객체
    all_loaded = Signal()  # 전체 로딩 완료
    error_occurred = Signal(str)

    def __init__(self, base_dir):
        super().__init__()
        self.base_dir = base_dir
        self._dummy_callback = lambda x: None  # 더미 콜백 함수

    def run(self):
        try:
            print("[AILoader Thread] AI 로딩 스레드 시작")
            
            # 1. 채팅 모델 로딩
            print("[AILoader Thread] 채팅 모델 로딩 시작...")
            # time.sleep(2)  # 비동기 확인용 시뮬레이션
            
            chat_controller = get_chat_controller(result_callback=self._dummy_callback)
            self.model_loaded.emit("chat", chat_controller)
            print("[AILoader Thread] 채팅 모델 로딩 완료")
            
            # 2. 이미지 생성 모델 로딩
            print("[AILoader Thread] 이미지 생성 모델 로딩 시작...")
            # time.sleep(2)  # 비동기 확인용 시뮬레이션
            
            text_encoder_path = os.path.join(self.base_dir, "data", "models", "text_encoder.onnx", "model.onnx")
            vae_decoder_path = os.path.join(self.base_dir, "data", "models", "vae_decoder.onnx", "model.onnx")
            unet_path = os.path.join(self.base_dir, "data", "models", "unet.onnx", "model.onnx")
            
            print("[AILoader Thread] 이미지 생성 엔진 초기화 중...")
            image_gen_engine = QStableV21Engine(
                text_encoder=text_encoder_path,
                vae_decoder=vae_decoder_path,
                unet=unet_path,
                scheduler="ddim",
                channel_last_latent=True
            )
            self.model_loaded.emit("image_gen", image_gen_engine)
            print("[AILoader Thread] 이미지 생성 모델 로딩 완료")
            
            # 3. 이미지 인식 모델 로딩
            print("[AILoader Thread] 이미지 인식 모델 로딩 시작...")
            # time.sleep(2)  # 비동기 확인용 시뮬레이션
            img_to_text_engine = DummyImgToTextEngine()
            self.model_loaded.emit("img_to_text", img_to_text_engine)
            print("[AILoader Thread] 이미지 인식 모델 로딩 완료")
            
            # 4. 모든 로딩 완료
            self.all_loaded.emit()
            print("[AILoader Thread] 모든 AI 모델 로딩 완료, AI 로딩 스레드 종료")
            
        except Exception as e:
            print(f"[AILoader Thread] 오류 발생: {e}")
            self.error_occurred.emit(str(e))