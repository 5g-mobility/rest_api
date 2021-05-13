from client.client import Client
from utils.video_stream import VideoStream
import argparse
import time

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    rtsp_user_agent = "RTSP Client"
    rtsp_user = None
    rtsp_pw = None

    parser.add_argument('--host_file_path', help='File Path to be included in Host Address', nargs='+', type=str)
    parser.add_argument('--host_address', help='Host Address', nargs='+', type=str)
    parser.add_argument('--host_port', help='Host Port', nargs='+', type=int)
    parser.add_argument('--rtp_port', help='RTP Port to receive frames', nargs='+', type=int)
    parser.add_argument('--rtsp_user', help='RTSP User for Authentication', nargs='?', type=str, default=None)
    parser.add_argument('--rtsp_pw', help='RTSP Password for Authentication', nargs='?', type=str, default=None)
    parser.add_argument('--rtsp_user_agent', help='Custom RTSP User Agent', nargs='?', type=str, default='RTSP Client')

    args = parser.parse_args()

    if len(args < 4):
        print("Insufficient arguments")
        quit()

    media_client = Client(args.host_file_path[0], args.host_address[0], args.host_port[0], args.rtp_port[0], args.rtsp_user, args.rtsp_pw, args.rtsp_user_agent)
    media_client.establish_rtsp_connection()
    media_client.send_describe_and_authenticate_request()
    media_client.send_setup_request()
    media_client.send_play_request()
    time.sleep(5)
    media_client.send_teardown_request()
    time_between_updates_image = 1000//VideoStream.DEFAULT_FPS

