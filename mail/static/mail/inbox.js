document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  // Send an email
  document.querySelector('#compose-form').onsubmit = send_email;
});

function clear_DOM(){
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#emails').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-page').style.display = 'none';
}
function compose_email() {

  // Show compose view and hide other views
  clear_DOM();
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  clear_DOM()
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#emails').style.display = 'block';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    //console.log(emails)
    var node= document.getElementById("emails");
    node.querySelectorAll('*').forEach(n => n.remove());
    for (email in emails) {
      //get the current email
      const c_email = emails[email];
      // create html element for email and its components 
      const div = document.createElement('div');
      div.classList = 'email-preview row alert';
      const email_id = document.createElement('p');
      email_id.innerHTML = c_email.id;
      email_id.style.display = 'none';
      const time = document.createElement('div');
      time.classList = 'col-3 date';
      time.innerHTML = c_email.timestamp;
      const subject = document.createElement('div');
      subject.className = 'col-6 ';      
      subject.innerHTML = c_email.subject;
      const adress =  document.createElement('div');
      adress.className = 'col-3';
      adress.innerHTML = c_email.sender;
      if (c_email.read){
        div.classList.add("alert-dark");
      }
      else{
        div.classList.add("alert-info");
      }
      div.append(adress);
      div.append(subject);
      div.append(time);
      div.append(email_id);
      div.addEventListener('click', load_email);
      node.append(div);
    }
  })

}


function send_email() {
  const r = document.querySelector('#compose-recipients').value;
  const s = document.querySelector('#compose-subject').value;
  const b = document.querySelector('#compose-body').value;
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: r,
      subject: s,
      body: b,
    })
  })
  .then(response => response.json())
  .then(result => {
    console.log(result);
  });
  // show user their sent emails
  load_mailbox('sent');
  return false;
}

function load_email() {
  clear_DOM();
  var node= document.getElementById("email-page");
  node.querySelectorAll('*').forEach(n => n.remove());
  node.style.display = 'block';
  const email_id = this.childNodes[3].innerHTML;
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    console.log(email);
    const sender = document.createElement("h4");
    sender.innerHTML= `Sender: ${email.sender}`;
    const recipients = document.createElement("ul")
    const recipients_string = document.createElement('h5');
    recipients_string.innerHTML = "Recipients";
    for (r in email.recipients){
      const li = document.createElement('li');
      li.innerHTML = email.recipients[r];
      recipients.append(li);
    }
    const time = document.createElement('div');
    time.innerHTML = email.timestamp;
    const body = document.createElement('div');
    body.innerHTML = email.body;
    node.append(sender);
    node.append(recipients_string);
    node.append(recipients);
    node.append(time);
    node.append(body);    
    const my_email = document.querySelector('#my_email').innerHTML
    const archive = document.createElement('button');
    if (email.sender != my_email) {
      archive.className = 'archive_button';
      if (email.archived){
        archive.innerHTML = 'Unarchive'
      }
      else{
        archive.innerHTML = 'Archive'
      }
      archive.addEventListener('click', function(){
        if (email.archived){
          fetch(`/emails/${email_id}`, {
            method: 'PUT',
            body: JSON.stringify({
              archived: false
            })
          })
          .then(load_mailbox('inbox'))
        }
        else{
          fetch(`/emails/${email_id}`, {
            method: 'PUT',
            body: JSON.stringify({
              archived: true
            })
          })
          .then(load_mailbox('inbox'))
        }
        
      })
      node.append(archive);
      const reply = document.createElement('button');
      reply.className = 'reply';
      reply.innerHTML = 'reply';
      reply.addEventListener('click', function() {
        compose_email();
        document.querySelector('#compose-recipients').value = email.sender;
        if (email.subject[0] === 'R' || email.subject[1] ==='e' || email.subject[2]===':') {
          document.querySelector('#compose-subject').value = email.subject;
        }
        else{
          document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
        }
        document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
      })
      node.append(reply)
    }
  });

  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  })
}
