import bge
cont = bge.logic.getCurrentController()
own = cont.owner

own["low_fps"]=min(bge.logic.getAverageFrameRate(),own["low_fps"])