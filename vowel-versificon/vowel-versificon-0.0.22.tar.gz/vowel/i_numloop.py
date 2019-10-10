Ans="""

[{"id":"aa6daed4.1bbad8","type":"tab","label":"Flow 1","disabled":false,"info":""},{"id":"a7a70a8a.eed708","type":"inject","z":"aa6daed4.1bbad8","name":"","topic":"","payload":"","payloadType":"date","repeat":"","crontab":"","once":false,"onceDelay":0.1,"x":283.26666259765625,"y":286,"wires":[["54e101b0.5a08e8"]]},{"id":"664784a6.08df24","type":"debug","z":"aa6daed4.1bbad8","name":"","active":true,"tosidebar":true,"console":false,"tostatus":false,"complete":"payload","targetType":"msg","x":717.2666015625,"y":298.6166687011719,"wires":[]},{"id":"54e101b0.5a08e8","type":"function","z":"aa6daed4.1bbad8","name":"","func":"for(i=0;i<=10;i++)\n{\n node.send({payload:i})   \n}","outputs":1,"noerr":0,"x":499.2666320800781,"y":291.3666687011719,"wires":[["664784a6.08df24"]]}]

"""