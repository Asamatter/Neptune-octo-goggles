function moveToNextField(event, nextFieldId) {
  if (event.key === "Enter") {
    event.preventDefault(); 
    document.getElementById(nextFieldId).focus();
  }
}  


function goBack() {
  window.history.go(-1); // Go back to the previous page
}



//detail
document.addEventListener('DOMContentLoaded', function() {
  const settingscard = document.getElementById('SettingsDetailCard');
  const settingstoggle = document.getElementById('settingsToggle');

  settingstoggle.addEventListener('click', function(event) {
    event.stopPropagation();
    settingscard.classList.toggle('active');
  });

  document.addEventListener('click', function(event) {
    if (!settingstoggle.contains(event.target)) {
      settingscard.classList.remove('active');
    }
  });
});




////SEARCH
document.getElementById('search-form').addEventListener('submit', function(event) {
  event.preventDefault(); // Prevent form submission

  var query = document.getElementById('search-input').value;
  var url = '/search/?query=' + encodeURIComponent(query);

  // Make an AJAX request to the server
  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
      if (xhr.readyState === 4 && xhr.status === 200) {
          document.getElementById('search-results').innerHTML = xhr.responseText;
      }
  };
  xhr.open('GET', url, true);
  xhr.send();
});

document.addEventListener('click', function(event) {
  const searchResults = document.getElementById('search-results');
  const searchForm = document.getElementById('search-form');

  // Check if the click target is outside the search area
  if (!searchResults.contains(event.target) && !searchForm.contains(event.target)) {
      searchResults.innerHTML = ''; // Clear the search results
  }
});




///settings
document.addEventListener('DOMContentLoaded', function() {
  const settingsButton = document.getElementById('settingsButton');
  const settingsCard = document.getElementById('settingsCard');

  // Event listener to toggle the settings card when the button is clicked
  settingsButton.addEventListener('click', function(event) {
    event.stopPropagation(); // Prevent the click event from propagating to the window
    settingsCard.classList.toggle('hidden');
  });

  // Event listener to close the settings card when clicking outside of it
  window.addEventListener('click', function(event) {
    if (!settingsCard.contains(event.target)) {
      settingsCard.classList.add('hidden'); // Hide the card
    }
  });
});




///BOOKMARK UPDATE 

$(document).ready(function() {
  $('.bookmark-form').on('submit', function(event) {
    event.preventDefault(); 

    const form = $(this);
    const url = form.attr('action');
    const csrftoken = form.find('[name=csrfmiddlewaretoken]').val();
    const bookmarkId = form.closest('.bg-gray-800').attr('id'); // Get the ID of the bookmark element
    $('#loading-content').show();
    // Create the AJAX request
    $.ajax({
      type: 'POST',
      url: url,
      data: form.serialize(), 
      headers: {
        'X-CSRFToken': csrftoken
      },
      dataType: 'json',
      success: function(response) {

        console.log('Success:', response); // Log the response

        // Remove the bookmark element from the page after successful deletion
        if (!response.bookmark_added) {
          $('#' + bookmarkId).remove(); // Remove the element from the DOM
        }

          const bookmarkCount = response.bookmark_user_count;

          console.log('Bookmark Counte', bookmarkCount);

          $('.bookmark-count').text(bookmarkCount); 
          $('#loading-content').hide();

      },
  

    });
  });
 
});



///HOMEPAGE BOOKMARK
var handleBookmarkHome = function(event) {
  event.preventDefault(); 
  var form = $(this);
  var url = form.attr('action');
  $('#loading-content').show();

  $.ajax({
    type: 'POST',
    url: url,
    data: form.serialize(),
    headers: {
      'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val()
    },
    success: function(response) {
      console.log('Success - Response:', response);

      var bookmarkHomeCount = form.closest('.flex').find('.bookmark-count-home');
      bookmarkHomeCount.text(response.post_bookmark_count);
      $('#loading-content').hide();
    }
  });
};

$(document).ready(function() {
  $(document).on('submit', '.bookmark-form-mainpage', handleBookmarkHome);
});








///VOTING  
$(document).on('click', '.choice-button', function(event) {
  event.preventDefault();
  var button = $(this);
  var form = button.closest('.vote-form');
  var url = form.attr('action');
  var postSlug = form.find('[name="post_slug"]').val();
  var choiceId = button.val();
  var choiceTitle = button.data('choice-title');
  $('#loading-content').show();

  console.log('Submitting vote data:', { post_slug: postSlug, choice: choiceId, title: choiceTitle });

  $.ajax({
      type: 'POST',
      url: url,
      data: { post_slug: postSlug, choice: choiceId, title: choiceTitle},
      headers: {
        'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val()
      },
      dataType: 'json',
      success: function(response) {

          console.log('Vote Response:', response);
          if (response.success) {
              const voteCountElement = form.find(`[data-choice="${choiceId}"]`);
              voteCountElement.text(response.vote_count);
              $('#post-template').load(window.location.href + ' #post-template > *');
                $('#loading-content').hide();
          } else {
              alert(response.error);
          }
      },
      error: function( error) {
          console.error('Error:', error);
      }
  });
});




///UPVOTE AND DOWNVOTE
var handleVoteFormSubmission = function(event) {
  event.preventDefault();
  var form = $(this);
  var url = form.attr('action');
  $('#loading-content').show();

  $.ajax({
    type: 'POST',
    url: url,
    data: form.serialize(),
    headers: { 'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val()},
    success: function(response) {
 
    var upvoteCount = form.closest('.flex').find('.upvote-count');
    upvoteCount.text(response.upvote_count);
    var downvoteCount = form.closest('.flex').find('.downvote-count');
    downvoteCount.text(response.downvote_count);
    $('#loading-content').hide();

    console.log('Vote Success:', response);
    },
    error: function(error) {
      console.log('Vote Error:', error);
    }
  });
};

$(document).ready(function() {
  $(document).on('submit', '.upvote-form, .downvote-form', handleVoteFormSubmission);
});





// FORM-POST-MAINPAGE ${HOME}
$(document).ready(function() {
  $('#form-post-mainpage').submit(function(event) {
    event.preventDefault(); 
    var form = $(this); 
    var url = form.attr('action'); 
    $('#loading-content').show();


    $.ajax({
      type: 'POST',
      url: url,
      data: form.serialize(), 
      dataType: 'html', 
      success: function(response) {
        console.log('Response:', response);
        if (response) {
          console.log('Form submitted successfully');
          $('#loading-content').hide();
          $(document).find('#post-template').load(window.location.href + ' #post-template > *');
      }
      },
     });
    form.trigger('reset');
  });
});


function refreshDetailPage(callback) {
    $.ajax({
        type: 'GET',
        url: window.location.href,
        success: function (response) {
            const updatedDetailHtml = $(response).find('.detail_page').html();
            $('.detail_page').html(updatedDetailHtml);
            console.log('Detail page updated');
            if (callback) {
              callback();
          } },
        error: function () {
        } });
}



///COMMENT-FORM ${post_detail}
function postComment(form) {
  return new Promise(function(resolve, reject) {
    var url = form.attr('action');
    $.ajax({
      type: 'POST',
      url: url,
      data: form.serialize(),
      headers: { 'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val() },
      success: function(response) {
        console.log('Response:', response);
        if (response.success) {
          resolve('comment was successfully posted');
        } else {
          reject('there was an issue with the comment posting');
        }
      },
      error: function() {
        reject('error'); 
      }
    }); });
}
$(document).on('submit', '.comment-form', function(e) {
  e.preventDefault();
  var form = $(this);
  $('#loading-content').show();

  postComment(form)
    .then(function() {
      form.trigger('reset');
      $('#loading-content').hide();
      return $('#post-template').load(window.location.href + ' #post-template > *');

    })
    .catch(function() {
      $('#loading-content').hide();
      console.error('Comment posting failed.');
    });
});


///COMMENT-FORM-DELETE ${post_detail}
// delete a comment and return a promise
function deleteComment(form) {
  return new Promise(function(resolve, reject) {
    var url = form.attr('action');
    $.ajax({
      type: 'POST',
      url: url,
      data: form.serialize(),
      headers: { 'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val() },
      success: function(response) {
        console.log('Response:', response);
        if (response.success) {
          resolve('Comment deleted successfully');
        } else {
          reject('Comment deletion failed');
        }
      },
      error: function() {
        reject('Comment deletion encountered an error');
      }
    }); });
}
$(document).on('submit', '.comment-delete', function(event) {
  event.preventDefault();
  var form = $(this);
  $('#loading-content').show();

  deleteComment(form)
    .then(function() {
      $('#loading-content').hide();
      console.log('Comment deleted successfully.');
      return $('#post-template').load(window.location.href + ' #post-template > *'); })
    .catch(function() {
      $('#loading-content').hide();
      console.error('Comment deletion failed.'); }); });


// SHOW/HIDE-REPLY-TO-COMMENT-FORM ${post_detail}
$(document).ready(function () {
  $(document).on('click', '.reply-link', function (e) {
    e.preventDefault();
    const commentId = $(this).data('comment-id');
    const commentFormToggle = $(`.reply-form[data-comment-id="${commentId}"]`);
    $('.reply-form').not(commentFormToggle).addClass('hidden'); 
    commentFormToggle.toggleClass('hidden');  }); });

  $(document).on('click', function (e) {
    if (!$(e.target).closest('.reply-link').length && !$(e.target).closest('.reply-form').length) {
      $('.reply-form').addClass('hidden'); }  });

  function captureCommentId(element) {
    var CommentContent = element.textContent; 
    console.log('reply to comment Content:', CommentContent);}

// REPLY-TO-COMMENT-FORM-SUBMIT ${post_detail}
  $(document).on('submit', '.reply-form', function (e) {
    e.preventDefault(); 
    var form = $(this); 
    $('#loading-content').show();
    var url = form.attr('action');

    var CommentContent = form.find('input[name="reply_content"]').val();
    var commentUsername = form.find('input[name="comment_username"]').val();
    var currentUserUsername = form.find('input[name="current_user"]').val(); 
    var contentInput = form.find('input[name="content"]');
    var content = contentInput.val();

    if (commentUsername !== currentUserUsername) {
      var newContent = 'to:' + commentUsername + ' ' + content;
      contentInput.val(newContent);} 
    else {
      contentInput.val(content);  }
   
    $.ajax({
      type: 'POST',
      url: url,
      data: form.serialize() + '&reply_content=' + CommentContent,
      headers: {'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val()},
      success: function (response) {
        console.log('Response:', response);
        if (response.success) {
          console.log('Reply submitted successfully');
          $('#post-template').load(window.location.href + ' #post-template > *');
          $('#reply-content').val('');
          $('.reply-form-container').addClass('hidden');
          $('#loading-content').hide();
        } },  }); });

  

// REPLY-FORM-TOGGLE ${post_detail}
$(document).ready(function () {
  // Show/hide form when clicking "Reply" 
  $(document).on('click', '.reply-link-sub', function (e) {
    e.preventDefault();
    const replyId = $(this).data('reply-id');
    const replyFormToggle= $(`.replyToReplyForm[data-reply-id="${replyId}"]`);
   
    $('.replyToReplyForm').not(replyFormToggle).addClass('hidden'); // Hide other open forms
    replyFormToggle.toggleClass('hidden'); // Toggle the 'hidden' class
  });
});

 // Hide reply form when clicking outside or inside any form field
 $(document).on('click', function (e) {
  if (!$(e.target).closest('.reply-link-sub').length && !$(e.target).closest('.replyToReplyForm').length) {
    $('.replyToReplyForm').addClass('hidden'); } });

    function captureReplyId(element) {
  var replyContent = element.textContent; 
  console.log('Reply to reply Content:', replyContent);
  
}

 
  

// REPLY-TO-REPLY-FORM ${post_detail}
$(document).on('submit', '.replyToReplyForm', function (e) {
  e.preventDefault();
  var form = $(this);
  var url = form.attr('action');
  $('#loading-content').show();

 
  var isReplyToReply = form.find('input[name="reply_id"]').val() !== form.find('input[name="comment_id"]').val();
  

  if (isReplyToReply) {

    var replyContent = form.find('input[name="reply_content"]').val()
    console.log('Reply IDR:', replyContent);

    var currentUserUsername = form.find('input[name="current_user"]').val(); 
    var replyUsername = form.find('input[name="reply_username"]').val();
    var contentInput = form.find('input[name="content"]');
    var content = contentInput.val();

    if (replyUsername !== currentUserUsername) {
          
        
      var newContent = 'to:' + replyUsername + ' ' + content;
      contentInput.val(newContent);
    } else {
      contentInput.val(content);
    }

    // Modify the content to ensure only one "to:" prefix exists
    var modifiedContent = contentInput.val().replace(/to:.*?\sto:/, 'to:');
    contentInput.val(modifiedContent);  }

  $.ajax({
    type: 'POST',
    url: url,
    data: form.serialize() + '&reply_content=' + replyContent,
  
    
    headers: {'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val()},
    success: function (response) {
      console.log('Response:', response);
      if (response.success) {


        $('.replyToReplyForm').addClass('hidden');
        var commentId = form.closest('.my-3').data('comment-id');
        $(document).find(`[data-comment-id="${commentId}"] #reply_container`).load(window.location.href + ` [data-comment-id="${commentId}"] #reply_container > *`);
         $('#loading-content').hide();    
      } }
  }); });


// REPLY-DELETE-FORM ${post_detail}  
function deleteReply(form) {
  return new Promise(function(resolve, reject) {
    var url = form.attr('action');
    $.ajax({
      type: 'POST',
      url: url,
      data: form.serialize(),
      headers: { 'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val() },
      success: function(response) {
        console.log('Response:', response);
        if (response.success) {
          resolve('Comment deleted successfully');
        } else {
          reject('Comment deletion failed');
        }
      },
      error: function() {
        reject('Comment deletion encountered an error');
      }
    }); });
}
$(document).on('submit', '.reply_delete', function(event) {
  event.preventDefault();
  var form = $(this);
  $('#loading-content').show();

  deleteReply(form)
    .then(function() {
      $('#loading-content').hide();
      console.log('Comment deleted successfully :)');
      return $('#post-template').load(window.location.href + ' #post-template > *'); })
    .catch(function() {
      $('#loading-content').hide();
      console.error('Comment deletion failed.'); }); });




///message form


function updateMessageContainer() {
  $('#message-container').load(window.location.href + ' #message-container > *');
}

$(document).on('submit', '.message-form', function(event) {
  event.preventDefault();
  var form = $(this);
  $('#loading-content').show();

  submitMessage(form)
    .then(function() {
      $('#loading-content').hide();
      console.log('message sent successfully :)');
      return $('#message-container').load(window.location.href + ' #message-container > *'); })
    .catch(function() {
      $('#loading-content').hide();
      console.error('message failed.'); }); });

      function submitMessage(form) {
        return new Promise(function(resolve, reject) {
          var url = form.attr('action');
          $.ajax({
            type: 'POST',
            url: url,
            data: form.serialize(),
            headers: { 'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val() },
            success: function(response) {
              console.log('Response:', response);
              if (response.success) {
                resolve('message submitted successfully');
                updateMessageContainer();
                form.trigger('reset');
              } else {
                reject('message failed');
              }
            },
            error: function() {
              reject('message encountered an error');
            }
          }); });
      }      
      setInterval(updateMessageContainer, 5000);



  

const myDiv = document.getElementById("bottom_bar");
      let isScrolling;
    
      window.addEventListener("scroll", function () {
        // Clear the timeout while the user is still scrolling
        clearTimeout(isScrolling);
        
        myDiv.classList.add("hidden");
        
        isScrolling = setTimeout(function() {
          myDiv.classList.remove("hidden");
        }, 500); 
      });



//PROFILE-PIC-DELETE-FORM ${Edit}
function deleteProfilepic(form) {
  return new Promise(function(resolve, reject) {
    var url = form.attr('action');
    $.ajax({
      type: 'POST',
      url: url,
      data: form.serialize(),
      headers: { 'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val() },
      success: function(response) {
        console.log('Response:', response);
        if (response.success) {
          resolve('pic deleted successfully');
        } else {
          reject('pic deletion failed');
        }
      },
      error: function() {
        reject('pic deletion encountered an error');
      }
    }); });
}
$(document).on('submit', '.profile-pic-delete-form', function(event) {
  event.preventDefault();
  var form = $(this);
  $('#loading-content').show();

  deleteProfilepic(form)
    .then(function() {
      $('#loading-content').hide();
      console.log('pic deleted successfully :)');
      return $('#post-template').load(window.location.href + ' #post-template > *'); })
    .catch(function() {
      $('#loading-content').hide();
      console.error('pic deletion failed.'); }); });

 
//DELETE-BANNER ${Edit}
function deleteBanner(form) {
  return new Promise(function(resolve, reject) {
    var url = form.attr('action');
    $.ajax({
      type: 'POST',
      url: url,
      data: form.serialize(),
      headers: { 'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val() },
      success: function(response) {
        console.log('Response:', response);
        if (response.success) {
          resolve('banner deleted successfully');
        } else {
          reject('banner deletion failed');
        }
      },
    }); });
}
$(document).on('submit', '.delete-banner', function(event) {
  event.preventDefault();
  var form = $(this);
  $('#loading-content').show();

  deleteBanner(form)
    .then(function() {
      $('#loading-content').hide();
      return $('#post-template').load(window.location.href + ' #post-template > *'); })
    .catch(function() {
      $('#loading-content').hide();
      console.error('pic deletion failed.'); }); });



//FOLLOW ${Profile}
function Follow(form) {
  return new Promise(function(resolve, reject) {
    var url = form.attr('action');
    $.ajax({
      type: 'POST',
      url: url,
      data: form.serialize(),
      headers: { 'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val() },
      success: function(response) {
        console.log('Response:', response);
        if (response.success) {
          resolve('form submitted');
        } else {
          reject('failed');
        }
      },
    }); });
}
$(document).on('submit', '.follow-form', function(event) {
  event.preventDefault();
  var form = $(this);
  $('#loading-content').show();

  Follow(form)
    .then(function() {
      $('#loading-content').hide();
      return $('#post-template').load(window.location.href + ' #post-template > *'); })
    .catch(function() {
      $('#loading-content').hide();
      console.error('form failed.'); }); });


//STATUS
function Status(form) {
  return new Promise(function(resolve, reject) {
    var currentUrl = window.location.href;
    $.ajax({
      type: 'POST',
      url: currentUrl,
      data: form.serialize(),
      headers: { 'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val() },
      success: function(response) {
        console.log('Response:', response);
        if (response.success) {
          resolve('form submitted');
        } else {
          reject('failed');
        }
      },
    }); });
}
$(document).on('submit', '.status-form', function(event) {
  event.preventDefault();
  var form = $(this);
  $('#loading-content').show();

  Status(form)
    .then(function() {
      $('#loading-content').hide();
      return $('#status').load(window.location.href + ' #status > *'); })
    .catch(function() {
      $('#loading-content').hide();
      console.error('form failed.'); }); });


//RESPOST-FORM


//open-repost-card
let openCard = null;
function toggleDropdown(postId) {
  const buttonsDiv = document.getElementById('buttons-' + postId);

  if (openCard && openCard !== buttonsDiv) {
    openCard.classList.add('hidden');   }

  buttonsDiv.classList.toggle('hidden');
  openCard = buttonsDiv;  }

document.addEventListener('click', function (event) {
  let clickedOutside = true;
  document.querySelectorAll('[data-post-id]').forEach(function (card) {
    if (card.contains(event.target)) {
      clickedOutside = false;
    } });
  if (clickedOutside && openCard) {
    openCard.classList.add('hidden');
    openCard = null; 
  } });

//open-repost-qoute-input
let contentCard = null;
function showContentField(postId) {
  var contentField = document.getElementById('contentField-' + postId);
  
  if (contentCard && contentCard !== contentField) {
    contentCard.classList.add('hidden');   }

  contentField.classList.toggle('hidden');
  contentCard = contentField;

  if (openCard) {
    console.log("Closing open card:", openCard.id);
    openCard.classList.add('hidden');
    openCard = null; // Reset the open card reference
  }
}
  
document.addEventListener('click', function (event) {
  let clickedOutside = true;
  document.querySelectorAll('[data-post-id]').forEach(function (card) {
    if (card.contains(event.target)) {
      clickedOutside = false;
    } });
  if (clickedOutside && contentCard) {
    contentCard.classList.add('hidden');
    contentCard = null; 
  } });



//textarea



function Repost(form) {
  return new Promise(function(resolve, reject) {
    var url = form.attr('action');

    $.ajax({
      type: 'POST',
      url: url,
      data: form.serialize(),
      headers: { 'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val() },
      success: function(response) {
        console.log('Response:', response);
        if (response.success) {
          resolve('form submitted');
        } else {
          reject('failed');
        }
      },
    }); });
}

$(document).on('submit', '.repost-form', function(event) {
  event.preventDefault();
  var form = $(this);
  $('#loading-content').show();

  Repost(form)
    .then(function() {
      $('#loading-content').hide();
      return $('#post-template').load(window.location.href + ' #post-template > *'); })
    .catch(function() {
      $('#loading-content').hide();
      console.error('form failed.'); }); });





//JOIN-LEAVE-CIRCLE ${Profile}
function JoinLeaveCircle(form) {
  return new Promise(function(resolve, reject) {
    var url = form.attr('action');
    $.ajax({
      type: 'POST',
      url: url,
      data: form.serialize(),
      headers: { 'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val() },
      success: function(response) {
        console.log('Response:', response);
        if (response.success) {
          resolve('form submitted');
        } else {
          reject('failed');
        }
      },
    }); });
}
$(document).on('submit', '.join-leave-form', function(event) {
  event.preventDefault();
  var form = $(this);
  $('#loading-content').show();

  JoinLeaveCircle(form)
    .then(function() {
      $('#loading-content').hide();
      return $('#circle-template').load(window.location.href + ' #circle-template > *'); })
    .catch(function() {
      $('#loading-content').hide();
      console.error('form failed.'); }); });



function Like(form) {
        return new Promise(function(resolve, reject) {
          var url = form.attr('action');
          $.ajax({
            type: 'POST',
            url:url,
            data: form.serialize(),
            headers: { 'X-CSRFToken': form.find('input[name=csrfmiddlewaretoken]').val() },
            success: function(response) {
              console.log('Response:', response);
              if (response.success) {
                resolve('form submitted');
              } else {
                reject('failed');
              }
            },
          }); });
      }
      $(document).on('submit', '.like-form', function(event) {
        event.preventDefault();
        var form = $(this);
        $('#loading-content').show();
      
        Like(form)
          .then(function() {
            $('#loading-content').hide();
            return $('#circle-template').load(window.location.href + ' #circle-template > *'); })
          .catch(function() {
            $('#loading-content').hide();
            console.error('form failed.'); }); });