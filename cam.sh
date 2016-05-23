ffmpeg -v verbose -r 5 -s 640x480 -f video4linux2 -i /dev/video0 http://localhost/webcam.ffm
sudo ffserver -f ./ffserver.conf

