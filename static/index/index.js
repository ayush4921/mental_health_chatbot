$("#submit_button").click(function(event) {
    event.preventDefault();
    var name = $("#name").val();
    var dob = $("#dob").val();
    var gender = $("#gender").val();
    var weight = $("#weight").val();
    var height = $("#height").val();
    console.log(name, dob, gender, weight, height);
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
            $.ajax({
                data: {
                    name: name,
                    dob: dob,
                    gender: gender,
                    height: height,
                    weight: weight,
                    id: user.uid,
                    photoURL: user.photoURL,
                    email: user.email,
                },
                type: "POST",
                url: "/makeqrcodeandsetupfirebase",
            }).done(function(data) {
                $("#form1").hide();
                $("#result").html(
                    '<img id="myimg" width="100%" height="100%" src="/static/id_images/' +
                    user.uid +
                    '.png"/>'
                );
            });
        }
    });
    return false;
});