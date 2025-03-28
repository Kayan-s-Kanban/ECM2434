(function(){

    function getCSRFToken() {
        return document.cookie.match(/csrftoken=([^;]+)/)[1];
    }

    window.completeTask = function(element, taskId) {
        fetch(`/ecolution/tasks/complete/${taskId}/`, {
            method: 'POST',
            headers: { 
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                var pointsEl = document.querySelector(".currency_indicator h3");
                if (pointsEl) { 
                    pointsEl.innerText = data.points; 
                }
                // Removes task and reloads the page, spwans particles for a success animation
                var taskElement = element.closest(".task");
                if (taskElement) {
                    spawnParticles(taskElement, 60);
                    // Change the z-index to be above the particles
                    taskElement.style.zIndex = 2;
                    // Set a CSS transition for the opacity to fade out
                    taskElement.style.transition = "opacity ease-out 3s";
                    // Trigger the fade by setting opacity to 0
                    taskElement.style.opacity = "0";
                    taskElement.style.opacity
                    setTimeout(() => {
                        taskElement.remove();

                        if (window.location.href.includes("tasks")) {
                            window.location.href = "/ecolution/tasks/";
                        } else {
                            window.location.href = "/ecolution/home/";
                        }
                    }, 3000);
                }
                // if (window.location.href.includes("tasks")) {
                //     window.location.href = "/ecolution/tasks/";
                // } else {
                //     window.location.href = "/ecolution/home/";
                // }
            }
        })
        .catch(error => console.error('Error completing task:', error));
    };    
    

    window.deleteTask = function(element, userTaskId) {
        fetch(`/ecolution/tasks/delete/${userTaskId}/`, {
            method: 'POST',
            headers: { 
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                var taskElement = element.closest(".task");
                if(taskElement) { taskElement.remove(); }
            }
        })
        .catch(error => console.error('Error deleting task:', error));
    };
})();
