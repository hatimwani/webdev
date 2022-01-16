document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#following_request').addEventListener('click', follow);
});



function follow() {
  const f = document.querySelector('#following_request').value;
  const u = document.querySelector('#user_id').value;
  console.log("hello");
  fetch('/follow', {
    method: 'POST',
    body: JSON.stringify({
        user_id: u,
      }),
  })
  .then(response => response.json())
  .then(result => {
  console.log(result);
  });
  follow_button_value(f)
  return false;
}

function follow_button_value(current_status) {
  if (current_status == "follow"){
    document.getElementById("following_request").value = "unfollow"
  }
  else{
    document.getElementById("following_request").value = "follow"
  }
}

function like(v){
  console.log(v)
}
