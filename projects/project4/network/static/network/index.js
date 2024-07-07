document.addEventListener("DOMContentLoaded", () => {
  console.log("The Document Object Model has loaded.");

  follow();

  const submitPostButton = document.querySelector("#submit-post");

  submitPostButton?.addEventListener("click", () =>
    create_post()
  );

  const likeButton = document.querySelector("#like");

  likeButton.addEventListener("click", () =>
    like()
  );

  const editPostButton = document.querySelector("#edit-post");

  editPostButton?.addEventListener("click", () => {
    edit_post_form();

    save_edit();
  });
});

function create_post() {
  const createPostForm = document.getElementById("post-form");

  const content = createPostForm["content"].value;

  if (!content) return;

  fetch("/post/", {
    method: "POST",
    body: JSON.stringify({
      content
    })
  }).then((response) => response.json()).catch((error) => console.error(error));
}

function edit_post_form() {
  const editPostForm = document.getElementById("edit-post-form");

  editPostForm.classList.toggle("hidden");
  editPostForm.classList.toggle("visible");
}

async function edit_post() {
  const field = document.getElementById("edit-post-content");

  const new_content = field.value;

  if (!new_content) return;

  const editPostForm = document.getElementById("edit-post-form");

  const postId = editPostForm.getAttribute("data-post-id");

  try {
    await fetch("/update_post/" + postId + "/", {
      method: "PUT",
      body: JSON.stringify({
        content: new_content
      })
    });

    editPostForm.classList.add("hidden");

    editPostForm.classList.remove("visible");

    const content = document.getElementById("post-content");

    content.textContent = new_content;
  } catch (error) {
    console.error(error);
  }
}

function save_edit() {
  const saveEditButton = document.querySelector("#save-edit");

  saveEditButton.addEventListener("click", async () =>
    await edit_post()
  );
}

async function follow() {
  const button = document.getElementById("follow-unfollow");

  button?.addEventListener("click", async () => {
    const username = button.getAttribute("data-username");
    const action = button.getAttribute("data-action");

    fetch("/follow/" + username + "/", {
      method: action,
    }).then(() => window.location.reload());
  });
}

function like() {
  const likeButton = document.getElementById("like");

  const postId = likeButton.getAttribute("data-post-id");

  fetch("/like/" + postId + "/", {
    method: "POST",
    body: JSON.stringify({ "post_id": postId }),
  }).then(response => response.json())
    .then(data => {
      const count = document.getElementById("like");

      count.innerHTML = `&#x2665;&#xfe0f; ${data.likes}`;
    })
    .catch(error => console.error(error));
};
