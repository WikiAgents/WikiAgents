import os
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_DATABASE = os.environ["DB_DATABASE"]
DB_URL = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@bookstack-db:3306/{DB_DATABASE}"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)


Base = declarative_base()


class Setting(Base):
    __tablename__ = "settings"

    setting_key = Column(String(191), primary_key=True)
    value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    type = Column(String(50), default="string")


with SessionLocal() as session:
    if not session.query(Setting).filter_by(setting_key="app-name").first():
        session.add(Setting(setting_key="app-name", value="✨ WikiAgents"))
    if not session.query(Setting).filter_by(setting_key="app-editor").first():
        session.add(Setting(setting_key="app-editor", value="markdown"))
    if not session.query(Setting).filter_by(setting_key="app-logo").first():
        session.add(Setting(setting_key="app-logo", value="none"))
    if not session.query(Setting).filter_by(setting_key="app-custom-head").first():

        session.add(
            Setting(
                setting_key="app-custom-head",
                value="""<script>
  var replace = {
    "shelves": "projects",
    "shelf": "project"
  }

  let title = document.title.split("|").map(chunk => chunk.trim()); 
  if(replace[title[0].toLowerCase()]){
    document.title = capitalizeFirstLetter(replace[title[0].toLowerCase()]) + " | " + title[1];
  }
  
  var regex = new RegExp(Object.keys(replace).join("|"),"gi");

  function walkText(node) {
    if (node.className == "tri-layout-middle") {
        return;
    }

    if (node.nodeType == 3) {
      node.data = node.data.replace(regex, function(matched) {
        const replaced = replace[matched.toLowerCase()];

        if (matched.charAt(0) === matched.charAt(0).toUpperCase()) {
          return capitalizeFirstLetter(replaced);
        } else {
          return replaced;
        }
      });
    }

    if (node.nodeType == 1 && node.nodeName != "SCRIPT") {
      for (var i = 0; i < node.childNodes.length; i++) {
        walkText(node.childNodes[i]);
      }
    }
  }

  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  window.addEventListener('DOMContentLoaded', function(){
    walkText(document.body);
  });


document.addEventListener("DOMContentLoaded", function () {
    function monitorAndReloadPage(intervalMs = 3000) {
        // Selector for the current comment count and section
        const commentCountSelector = 'div[refs="page-comments@comment-count-bar"] h5';

        let currentCommentCount = null;
        let intervalId;  // Store the interval ID so we can clear it before reloading the page

        // Helper function to get the number of comments from the current page
        function getCommentCount() {
            const commentsTitleElement = document.querySelector(commentCountSelector);
            if (commentsTitleElement) {
                const commentsText = commentsTitleElement.textContent.trim();
                const commentsMatch = commentsText.match(/\d+/); // Match the first number
                if (commentsMatch) {
                    return parseInt(commentsMatch[0], 10);
                }
            }
            return 0;
        }

        // Initialize current comment count
        currentCommentCount = getCommentCount();

        // Helper function to fetch the page in the background and get the comment count
        async function fetchPageAndGetCommentCount() {
            try {
                const response = await fetch(window.location.href, {
                    method: 'GET',
                    headers: {
                        'Accept': 'text/html'
                    }
                });
                const text = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(text, 'text/html');

                // Extract the new comment count from the fetched page
                const commentsTitleElement = doc.querySelector(commentCountSelector);
                if (commentsTitleElement) {
                    const commentsText = commentsTitleElement.textContent.trim();
                    const commentsMatch = commentsText.match(/\d+/);
                    return commentsMatch ? parseInt(commentsMatch[0], 10) : 0;
                }
            } catch (error) {
                console.error('Error fetching the page in the background:', error);
                return currentCommentCount; // Return the current comment count if fetching fails
            }
            return 0; // Default to 0 if the comment count cannot be found
        }

        // Periodically fetch the page and check if the comment count has changed
        intervalId = setInterval(async () => {
            const newCommentCount = await fetchPageAndGetCommentCount();
            // If the comment count has changed, reload the page
            if (newCommentCount !== currentCommentCount) {                
                // Clear the interval to avoid further checks
                clearInterval(intervalId);
                // Reload the page
                window.location.reload(); // Reload the page
            }

            currentCommentCount = newCommentCount; // Update the current comment count
        }, intervalMs); // Check every `intervalMs` milliseconds
    }

    // Start monitoring the comment count and reload if there's a change
    monitorAndReloadPage();
});
</script>""",
            )
        )

    session.commit()
