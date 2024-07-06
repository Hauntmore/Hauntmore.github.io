document.addEventListener('DOMContentLoaded', function (event) {
  event.preventDefault();

  console.log("The Document Object Model has loaded.");

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));

  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));

  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));

  document.querySelector('#compose').addEventListener('click', compose_email);

  document.getElementById('compose-form-submit').addEventListener('click', async (event) =>
    await send_email());

  // By default, load the inbox
  load_mailbox('inbox');
});

async function send_email() {
  const recipients = document.querySelector('#compose-recipients').value;

  const subject = document.querySelector('#compose-subject').value;

  const body = document.querySelector("#compose-body").value;

  try {
    const response = await fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
      })
    });

    if (!response.ok) {
      document.getElementById("compose-message").innerHTML = "This recipient doesn't exist!";

      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    } else {
      load_mailbox("sent");
    }

    console.log(response);
  } catch (error) {
    console.error(error);
  }
}

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`, {
    method: 'GET'
  }).then((response) => response.json()).then((emails) => emails.forEach((email) => {

    const table = document.getElementById('emails-view');

    const a = document.createElement('a');

    // a.classList.add('email-link');

    a.innerHTML = `
      <div class="${email.read ? 'read' : 'unread'} row border m-1">
          <div class="col-sm-3 email-sender">
            ${email.sender}
          </div>

          <div class="col-sm-6 email-subject">
            ${email.subject || "No Subject"}
          </div>

          <div class="col-sm-3 email-timestamp">
            ${email.timestamp}
          </div>
      </div>
    `;

    a.addEventListener("click", () => load_email(email.id));

    table.append(a);

  })).catch((error) => console.error(error));
}

function load_email(id) {
  fetch(`/emails/${id}`)
    .then((response) => response.json())
    .then((email) => {
      const view = document.querySelector("#emails-view");

      view.innerHTML = null;

      const box = document.createElement("div");

      box.className = "card";

      box.innerHTML = `
        <div class="card-body" style="white-space: pre-wrap;">
          <b>
            Author
          </b>
            ${email.sender}
          <b>
            Recipients
          </b>
            ${email.recipients}
          <b>
            Subject
          </b>
            ${email.subject || "No Subject"}
          <b>
            Sent At
          </b>
            ${email.timestamp}
          <hr>
          ${email.body}
          </div>
      `;

      view.appendChild(box);

      const hr = document.createElement("hr");

      view.appendChild(hr);

      read(id);

      const row = document.createElement("div");

      row.classList.add("row-container");

      const reply = document.createElement("button");

      reply.innerText = "Reply";

      row.appendChild(reply);

      reply.addEventListener("click", () => reply_email(email));

      const archive = document.createElement("button");

      archive.innerText = email.archived ? "Unarchive" : "Archive";

      row.appendChild(archive);

      archive.addEventListener("click", () => archive_email(email.id, email.archived));

      view.appendChild(row);
    });
}

function archive_email(id, archive_state) {
  fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      archived: !archive_state,
    }),
  });

  load_mailbox("archive");
}

function read(id) {
  fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      read: true,
    }),
  });
}

function reply_email(email) {
  compose_email();

  console.log(email);

  let subject = email.subject;

  const sender = email.sender;

  const timestamp = email.timestamp;

  const body = email.body;

  if (!/^Re:/.test(subject)) subject = `Re: ${subject}`;

  document.querySelector("#compose-recipients").value = sender;

  document.querySelector("#compose-subject").value = subject;

  new_body = `On ${timestamp}, ${sender} Wrote:\n${body}\n`;

  document.querySelector("#compose-body").value = new_body;
};
