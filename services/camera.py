#!/usr/bin/env python3
from imutils.video import FileVideoStream
from cv2 import imencode
from signal import signal, SIGINT
from websockets.sync.server import serve
from websockets.exceptions import ConnectionClosed
from functools import partial
from uuid import uuid4
from threading import Lock, Thread, Condition
from queue import Queue, Empty

def fprint(msg):
    print(msg, flush=True)

def is_running(stop_cond):
    is_stopped = stop_cond.acquire(blocking=False)
    if is_stopped:
        stop_cond.release()
    return not is_stopped

def get_noblock(queue):
    try:
        return queue.get_nowait()
    except Empty:
        return None

def video_worker(clients_queue, frames_queue, stop_cond, cam = 0):
    video = FileVideoStream(cam).start()
    clients = []
    fprint("started video worker")

    while video.more():
        if not is_running(stop_cond):
            video.stop()
            break

        while (id := get_noblock(clients_queue)) is not None:
            if id in clients:
                clients.remove(id)
                fprint("removed client %s" % id)
            else:    
                clients.append(id)
                fprint("added new client %s" % id)
            clients_queue.task_done()

        frame = video.read()
        if frame is None: continue
        else:
            for client in clients:
                frames_queue.put((client, frame))
        
    fprint("stopped video worker")

def video_subscriber(websocket, clients_queue, frames_queue, stop_cond):
    id = uuid4()
    clients_queue.put(id)

    fprint("opened connection")
    while is_running(stop_cond):
        if (f := get_noblock(frames_queue)) is not None:
            if f[0] != id:
                frames_queue.put(f)
                frames_queue.task_done()

            else:
                frames_queue.task_done()
                (_, buffer) = imencode(".jpg", f[1])
                try:
                    websocket.send(bytes(buffer))
                except ConnectionClosed:
                    break
    websocket.close()
    clients_queue.put(id)
    fprint("closed connection")
    

def main(stop_cond):
    clients_queue = Queue()
    frames_queue = Queue()
    with serve(partial(video_subscriber, clients_queue=clients_queue, frames_queue=frames_queue, stop_cond=stop_cond), "127.0.0.1", 6969) as server:
        vw_handle = Thread(target=video_worker, args=(clients_queue, frames_queue, stop_cond), daemon=True)
        vw_handle.start()

        def on_signint(sig, frame):
            stop_cond.release()
            server.shutdown()
        signal(SIGINT, on_signint)

        server.serve_forever()
        vw_handle.join()

if __name__ == '__main__':
    stop_cond = Condition(lock=Lock())
    stop_cond.acquire()

    main(stop_cond)