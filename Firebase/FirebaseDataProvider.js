const firebase = require('firebase');
const net = require('net');
require('firebase/firestore');
const apiKey = require('./api');
const fs = require('fs');

//Konstanten
const SOCKETFILE = '/tmp/unix.sock';
const PENDING_UPDATES_PATH = "./Configuration/pendingUpdates.json"

//Firebase-App initialisieren
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

firebase.auth().signInWithEmailAndPassword("jbol14@tu-clausthal.de","1234567")
.then((_)=>{
    init();
})
.catch((error)=>{
    console.error(error);
})
function init(){
    const db = firebase.firestore();

    const serviceRef = db.collection('/company/FEOq6WEjsTOf1nV7SQMl7xla63P2/service');

//const services = companyReference.doc(services).where("address","==", "Leibnizstraße,10,Clausthal-Zellerfeld,38678").get()
    const services = serviceRef.where("address", "==", "Leibnizstraße,10,Clausthal-Zellerfeld,38678");

    let query = services.onSnapshot({includeMetadataChanges:true}, (service)=>{
        service.docChanges().forEach((box)=>{
            // console.log(box.id); // Test
            // let reducedData = {
            //     id : box.id,
            //     category : box.data().category
            // }
            // console.log(reducedData) // Test
            // addService(box.id, reducedData)
            if(box.type == "added"){
                let reducedData = {
                    id : box.doc.id,
                    category : box.doc.category
                }
                addService(box.doc.id,box.doc.data());

                // ---- Reservierungen
                db.collection("reservation").where("serviceID", "==", box.doc.id)
                .onSnapshot({includeMetadataChanges:true},(reservationCollection)=>{
                    reservationCollection.docChanges().forEach((change)=>{
                        // Reservierung wurde in der Datenbank hinzugefügt
                        if(change.type === 'added'){
                            console.log("Neue Reservierung"); // Test
                            //Listener auf Neue Reservierung setzen
                            db.collection("reservation").doc(change.doc.id)
                            .onSnapshot({includeMetadataChanges:true}, (reservation)=>{
                                if(reservation.data()){
                                    reducedReservation = reservation.data();
                                    delete reducedReservation.used;
                                    console.log("data: ", reducedReservation); //Test

                                    if(validReservation(reducedReservation)){
                                        // ----- Shares -----
                                        //Listener für Shares
                                        db.collection("sharing").where("reservationID", "==", reservation.id)
                                        .onSnapshot({includeMetadataChanges:true}, (shares)=>{
                                            shares.docChanges().forEach((change)=>{
                                                // Share wurde in der Datenbank hinzugefügt
                                                if(change.type == 'added'){
                                                    addShare(change.doc.id, change.doc.data());
                                                }
                                                else if(change.type == 'removed'){
                                                    deleteShare(change.doc.id);
                                                    console.log("Share", change.doc.id, "wird gelöscht");
                                                }
                                            });
                                        });
    
                                        console.log("gültige Reservierung", reservation.id, reducedReservation);
                                        addReservation(reservation.id, reducedReservation)
    
                                    }
    
                                    else{
                                        console.log("Reservierung abgelaufen", reservation.id); // Test
                                        deleteReservation(reservation.id);
                                    }

                                }
                            });
                        }
                        else if(change.type == 'removed'){
                            console.log("Reservierung ", change.doc.id, " wird geköscht");
                            deleteReservation(change.doc.id);
                        }
                    });
                });
                
            }
            else if(box.type == "removed"){
                console.log("Service ", box.doc.id, " wird gelöscht");
                deleteService(box.doc.id);
            }
        });
        
    });
}

function validReservation(reservation){
	timeNow = firebase.firestore.Timestamp.now();
	console.log(timeNow.toMillis(), reservation.resTill.toMillis())
	if(!reservation.companyHasDeleted && !reservation.userHasDeleted && timeNow < reservation.resTill){
		return true;
	}
	else{
		return false;
	}
}

function updateBoxServer(document){
	const client = net.createConnection({path: SOCKETFILE});
	client.on('connect', ()=>{
		console.log('Connected to Socket');
		console.log(document.id)
		client.end(JSON.stringify(document));
	});
	client.on('data', (data)=>{
		console.log(data.toString());
	});
	client.on('end',()=>{
		console.log('Disconnected from Socket');
	});
	client.on('error',(error)=>{
        writeToBackupFile(error,document);
        //console.error(error,document);
        

	});
}
//----- Elemente hinzufügen -----

function addReservation(reservationId, reservation){
	reservation.resFrom = reservation.resFrom.toMillis(); //Neu, in Millisekunden umwandeln
	reservation.resTill = reservation.resTill.toMillis(); //Neu, in Millisekunden umwandeln
	payload = {
		id : reservationId,
		type : "ADD_RESERVATION",
		payload : reservation
	}
	updateBoxServer(payload);
}

function addShare(shareId, shareData){
	payload = {
		id : shareId,
		type : "ADD_SHARE",
		payload : shareData
	}
	console.log(payload) //Test
	updateBoxServer(payload)
}

function addService(serviceId, service){
	payload = {
		id : serviceId,
		type : "ADD_SERVICE",
		payload : service
	}
	console.log(payload); // Test
    updateBoxServer(payload);
}

//----- Elemente entfernen -----------

function deleteReservation(reservationId){
	payload = {
		id:reservationId,
		type: "DELETE"
	};
	console.log(payload); //Test
	updateBoxServer(payload);
}

function deleteShare(shareId){
    payload = {
        id : shareId,
        type : "DELETE_SHARE"
    }
    console.log("Deleting Share");
    updateBoxServer(payload);
}

function deleteService(serviceId){
    payload = {
        id : serviceId,
        type : "DELETE_SERVICE"
    }
    console.log("Deleting Service");
    updateBoxServer(payload);
}

function writeToBackupFile(error,document){
    try{
        content = fs.readFileSync(PENDING_UPDATES_PATH)
    }
    catch(error){
        content = "[]";
        fs.writeFileSync(PENDING_UPDATES_PATH, content);
    }
    console.log(content);
    js = JSON.parse(content);
    console.log(typeof js);
    console.log("After Reading File", js);
    js.push(document);
    console.log("After appending",js)
    fs.writeFileSync(PENDING_UPDATES_PATH, JSON.stringify(js));
}
