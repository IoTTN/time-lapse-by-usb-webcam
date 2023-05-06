import cv2

def test_webcam():
    # Mở webcam.
    cap = cv2.VideoCapture(0)

    while True:
        # Đọc một khung hình từ webcam.
        ret, frame = cap.read()

        # Nếu không thể đọc được khung hình, thoát khỏi vòng lặp.
        if not ret:
            break

        # Hiển thị khung hình trong một cửa sổ.
        cv2.imshow('Webcam', frame)

        # Nếu người dùng nhấn phím 'q', thoát khỏi vòng lặp.
        if cv2.waitKey(1) == ord('q'):
            break

    # Giải phóng webcam và đóng cửa sổ hiển thị.
    cap.release()
    cv2.destroyAllWindows()
if __name__ == '__main__':
    test_webcam()
