$("#submit_button").click(function(event) {
    event.preventDefault();
    var chat = $("#chat").val();
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
            $.ajax({
                data: {
                    chat: chat,
                    id: user.uid,
                    author_name: user.displayName,
                    email: user.email,
                },
                type: "POST",
                url: "/analyze_text",
            }).done(function(data) {
                $("#form1").hide();
                $("#result").html(`<h1>Polarity: ${data.feedback_polarity}</h1>`);
            });
        }
    });
    return false;
});