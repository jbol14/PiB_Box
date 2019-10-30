// Imports
const firebase = require('firebase');
const net = require('net');
require('firebase/firestore');
const apiKey = require('./api');

// Konstanten
const SOCKETFILE = '/tmp/firebase-logger.sock';
const LOCATION = 'yti5YJIX1Cnw0Pek79en/';

// Firebase-App initialisieren
firebase.initializeApp({
    apiKey : apiKey.getKey(),
    projectId: 'raspi-python-test'
});

const db = firebase.firestore();

const locationReference = db.collection('/company/yDOcLJggM9S9nUNt1SuQ/location');

let socketServer = net.createServer();
socketServer.listen("./log.sock", ()=>{
    console.log("Listening");
});
socketServer.on("connection", (s)=>{
    s.on('data',(data)=>{
        str = data.toString();
        console.log("data recieved")
        console.log(str);
        js = JSON.parse(str);
        console.log(js);
        if (!js.reservationId || !js.counter){
            console.log("fehlerhaftes Objekt");
        }
        else{
            writeBack(js.reservationId,js.counter)
        }
    })
    console.log("Connection");
});
socketServer.on("data", (data)=>{
    console.log(data.toString());
});

// Funktion zum zuückschreiben des erhöhten Zählers
function writeBack(reservationId, serviceCounter){
    db.collection('reservation').doc(reservationId).update({counter : serviceCounter})
}

//writeBack('cRHI274cWpEej4dAIJR8',2) // Testen, funktioniert

// TODO: Socket implementieren
// TODO: Bei empfangenen Daten auf Socket writeBack Funktion ausführen