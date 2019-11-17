// TODO: vernünftig beenden, d.h Socket-File entfernen etc.

// Imports
const fs = require('fs');
const firebase = require('firebase');
const net = require('net');
require('firebase/firestore');
const apiKey = require('./api');

// Konstanten
const SOCKETFILE = '/tmp/firebase-logger.sock';
const LOCATION = 'yti5YJIX1Cnw0Pek79en/';

// Firebase-App initialisieren
firebase.initializeApp({
    apiKey: apiKey.getKey(),
    authDomain: "boxsystem-a20f5.firebaseapp.com",
    databaseURL: "https://boxsystem-a20f5.firebaseio.com",
    projectId: "boxsystem-a20f5",
    storageBucket: "boxsystem-a20f5.appspot.com",
    messagingSenderId: "43374441475",
    appId: "1:43374441475:web:28ffa1c300028d56fc8a36"
  }
);

firebase.auth().signInWithEmailAndPassword("jbol14@tu-clausthal.de","supersicher")
.then((_)=>{
    init();
})
.catch((error)=>{
    console.error(error);
})



//firebase.firestore().enablePersistence();

//const locationReference = db.collection('/company/yDOcLJggM9S9nUNt1SuQ/location');
function init(){
    let socketServer = net.createServer();

    //Falls der Socket bereits existiert: entfernen
    if(fs.existsSync(SOCKETFILE)){
        fs.unlinkSync(SOCKETFILE)
    } 

    socketServer.listen(SOCKETFILE, ()=>{
        console.log("Listening");
    });
    socketServer.on("connection", (s)=>{
        s.on('data',(data)=>{
            str = data.toString();
            console.log("data recieved")
            console.log(str);
            js = JSON.parse(str);
            console.log(js);
            if (!js.reservationId || !js.used){
                console.log("fehlerhaftes Objekt");
            }
            else{
                js.used.whenUsed = firebase.firestore.Timestamp.now();
                writeBack(js.reservationId,js.used);
            }
        });
        s.on("end", () => {
            console.log("connection terminated")
        });
        s.on("error", (error)=>{
            console.error(error);
        });
        console.log("Connection");
    });
    socketServer.on("data", (data)=>{
        console.log(data.toString());
    });
}
// Funktion zum zuückschreiben des erhöhten Zählers
function writeBack(reservationId, serviceCounter){
    console.log(serviceCounter);
    const db = firebase.firestore();
    db.collection('reservation').doc(reservationId).update({used : firebase.firestore.FieldValue.arrayUnion(serviceCounter)})
}