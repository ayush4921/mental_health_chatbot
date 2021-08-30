var fireBase = fireBase || firebase;
var hasInit = false;

var config = {
    apiKey: "AIzaSyBeoD9rRW8m6IbuNlVdcr5g0uJ7u_1M-qY",
    authDomain: "techblazers-293ce.firebaseapp.com",
    projectId: "techblazers-293ce",
    storageBucket: "techblazers-293ce.appspot.com",
    messagingSenderId: "934699070399",
    appId: "1:934699070399:web:64c91f0f90f7d2be3fa70a",
    measurementId: "G-DJ853G16E1",
};
if (!hasInit) {
    firebase.initializeApp(config);
    hasInit = true;
}

firebase.auth().onAuthStateChanged(function(user) {
    if (user) {
        // User is signed in.
    } else {
        thePath = window.location.href;
        const lastItem = thePath.substring(thePath.lastIndexOf("/") + 1);
        console.log(lastItem);
        if (lastItem != "") {
            alert("Please log in");
            window.location.replace("/");
        }
    }
});