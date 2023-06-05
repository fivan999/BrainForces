window.addEventListener('DOMContentLoaded', (event) => {
    const csrftoken = Cookies.get('csrftoken');
    document.querySelectorAll("img[id='like']").forEach(el => el.addEventListener(
      'click',
      function like_post(){
        var like_button = this;
        like_button.disabled = true;
        var options = {
          method: 'POST',
          headers: {'X-CSRFToken': csrftoken},
          mode: 'same-origin'
        }
        var url = like_button.dataset.link;
        var form_data = new FormData();
        form_data.append('action', like_button.dataset.action);
        options['body'] = form_data;

        fetch(url, options)
        .then(response => response.json())
        .then(
          data => {
            if (data['status'] === 200){
              var previous_action = like_button.dataset.action;
              var action = previous_action === 'like' ? 'unlike' : 'like';
              like_button.dataset.action = action;
              like_button.innerHTML = action;
              var like_count_elem = document.getElementById(`total-likes-${like_button.dataset.postid}`);
              var total_likes = parseInt(like_count_elem.innerHTML);
              like_button.src = previous_action === 'like' ? liked_src : unliked_src;
              like_count_elem.innerHTML = previous_action === 'like' ? total_likes + 1 : total_likes - 1;
            }
          }
        )
        like_button.disabled = false;
      }
    )
    )
  }
  )