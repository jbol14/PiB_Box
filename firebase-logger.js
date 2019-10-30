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

// Funktion zum zuückschreiben des erhöhten Zählers
function writeBack(reservationId, serviceCounter){
    db.collection('reservation').doc(reservationId).update({counter : serviceCounter})
}

writeBack('cRHI274cWpEej4dAIJR8',2) // Testen, funktioniert

// TODO: Socket implementieren
// TODO: Bei empfangenen Daten auf Socket writeBack Funktion ausführen