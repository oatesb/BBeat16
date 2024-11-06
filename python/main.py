
from song.song import SongBatchProcessor

Nirvana_Scene_Controller_USA_PATCH = 12

def main():
 
    songBatchProcessor = SongBatchProcessor(r'C:\Guitar\BBeat16\python\songs')
    songBatchProcessor.processAllSongs()

if __name__=="__main__":
    main()