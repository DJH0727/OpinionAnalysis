

const chatContainer = document.getElementById("main");
    let selectedFileName = '';
    let uniqueFileName = '';
    let cachedImageBase64 = '';

    function sendMessage() {
      const input = document.getElementById("chat-input");
      const text = input.value.trim();
      if (!text && !selectedFileName) return;

  // 展示用户消息
      const userMsg = document.createElement("div");
      userMsg.className = "message user";
    // 如果有 Base64 图片，插入图片在上方
    if (cachedImageBase64) {
      const imagePreview = document.createElement("img");
      imagePreview.src = cachedImageBase64;
      imagePreview.className = "message-image";
      userMsg.appendChild(imagePreview);
      // 显示一次后清除缓存，避免下次误判
      cachedImageBase64 = null;
    }
    else if (selectedFileName) {
        const fileIcon = document.createElement("img");
        const fileCategory = getFileCategoryByName(selectedFileName);
        fileIcon.src = `/static/img/type_${fileCategory}.svg`;
        fileIcon.alt = "file-icon";
        fileIcon.className = "message-file-icon";
        userMsg.appendChild(fileIcon);
        const fileName = document.createElement("span");
        fileName.textContent = selectedFileName;
        userMsg.appendChild(fileName);
    }

    // 创建消息文本内容
    const messageText = document.createElement("div");
    messageText.textContent = text;
    userMsg.appendChild(messageText);
    chatContainer.appendChild(userMsg);


 // 创建机器人消息容器（等待回复）
      const botMsg = document.createElement("div");
      botMsg.className = "message bot";
      chatContainer.appendChild(botMsg);

      input.value = "";
      input.focus();

      const sendBtn = document.getElementById("send-button");
      sendBtn.disabled = true;
      pollTaskStatus()
       $.ajax({
        type: "get",
        url: "/getReply/",
        data: {
          text: text,
          opType: "chat",
          fileName: uniqueFileName,
        },
           dataType: "json",
        success: function (response) {
            if (response.replyType === "text") {
                typeWriterEffect(botMsg, response.reply);
                //支持markdown语法
                //botMsg.innerHTML = marked.parse(response.reply);
            }
            else if (response.replyType === "image") {
                const img = document.createElement("img");
                img.src = response.reply;
                img.alt = "机器人回复的图片";
                img.className = "chat-image"; // 你可以在 CSS 里加样式
                botMsg.appendChild(img);

            }
            else if (response.replyType === "file") {
                const fileIcon = document.createElement("img");
                const fileCategory = getFileCategoryByName(response.reply);
                fileIcon.src = `/static/img/type_${fileCategory}.svg`;
                fileIcon.alt = "file-icon";
                fileIcon.className = "message-file-icon";
                botMsg.appendChild(fileIcon);
                const fileLink = document.createElement("a");
                fileLink.textContent = response.reply;
                fileLink.href = `/static/downloads/${encodeURIComponent(response.reply)}`;  // 文件下载链接，按实际调整
                fileLink.download = response.reply;  // 提示浏览器下载
                fileLink.style.cursor = "pointer";
                fileLink.style.color = "#0066cc";  // 可自定义样式
                fileLink.style.textDecoration = "underline";
                botMsg.appendChild(fileLink);
            }
            sendBtn.disabled = false;
            window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
        },
        error: function (xhr, status, error) {
          botMsg.textContent = "出错了：" + error;
          sendBtn.disabled = false;
        },
      });

      window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });


      document.getElementById("file-info").textContent = ''; // Clear file info
        clearFile(); // Clear file input
    }
    // 展示机器人消息
    function typeWriterEffect(element, text, speed = 10) {
      let i = 0;
      const interval = setInterval(() => {
        element.textContent += text[i];
        i++;
        window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
        if (i >= text.length) clearInterval(interval);
      }, speed);
    }


function updateHeaderStatus(statusText) {
  const headerTitle = document.getElementById("header-title");
  headerTitle.textContent = `舆情分析聊天机器人（${statusText}）`;
}

function pollTaskStatus() {
  const intervalId = setInterval(function() {
    $.ajax({
      type: "get",
      url: "/getReplyStatus/",
      dataType: "json",
      success: function(response) {
         if (response.replyStatus === "finished") {
            clearInterval(intervalId);
           updateHeaderStatus("空闲中");}
         else  {
            updateHeaderStatus(response.replyStatus);
         }
      },
      error: function() {
        clearInterval(intervalId);
        updateHeaderStatus("空闲中");
      }
    });
  }, 1000);
}



    //监听按键，enter发送消息
    document.getElementById("chat-input").addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        sendMessage();

      }
    });


    //监听文件上传
    document.getElementById("file-input").addEventListener("change", function () {
      const file = this.files[0];
      if (file) {
          document.getElementById("send-button").disabled = true;
          const filename = file.name;
          selectedFileName = filename;
          const fileCategory = getFileCategory(file);

        document.getElementById("file-info").innerHTML = `
          <img src="/static/img/type_${fileCategory}.svg" alt="file-icon" />
          <span>${filename}</span>
           <button onclick="uploadFile()" 
          style="border:none; background:none; color:#8adcff; font-size:14px; cursor:pointer;
          margin-left: 10px;">
          上传
          </button>
          <button onclick="clearFile()" 
          style="border:none; background:none; color:#8adcff; font-size:14px; cursor:pointer;
          margin-left: 10px;">
          取消
          </button>`;

      }
    });


    //清除文件
    function clearFile() {
      document.getElementById("file-input").value = '';
      document.getElementById("file-info").textContent = '';
      document.getElementById("send-button").disabled = false;
      selectedFileName = ''; // Clear file name
        uniqueFileName = ''; // Clear file name
        cachedImageBase64 = ''; // Clear cached image
    }



    //上传文件
    function uploadFile() {

          const fileInput = document.getElementById("file-input");
          const file = fileInput.files[0];
          if (!file) return;
          if (file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = function (e) {
              // 存入缓存
            cachedImageBase64 = e.target.result;
          };
          reader.readAsDataURL(file);
        }

          const uploadBtn = document.querySelector("#file-info button[onclick='uploadFile()']");
          uploadBtn.disabled = true;

          // 创建进度条元素
          uploadBtn.innerHTML = `<span class="loading-spinner"></span> 上传中... <span id="upload-progress">0%</span>`;

          const formData = new FormData();
          formData.append("file", file);


          const xhr = new XMLHttpRequest();
          xhr.open("POST", "/uploadFile/", true);


          // 上传进度事件
          xhr.upload.onprogress = function (event) {
            if (event.lengthComputable) {
              const percent = Math.round((event.loaded / event.total) * 100);
              document.getElementById("upload-progress").innerText = `${percent}%`;
            }
          };

          // 上传完成
          xhr.onload = function () {
            if (xhr.status === 200) {
              uploadBtn.innerText = "上传成功";
              const response = JSON.parse(xhr.responseText);
              uniqueFileName = response.filename;
            } else {
              uploadBtn.innerText = "上传失败";
              uploadBtn.disabled = false;
            }
          };

          // 上传失败
          xhr.onerror = function () {
            alert("上传出错，请稍后再试！");
            uploadBtn.innerText = "上传";
            uploadBtn.disabled = false;
          };

          xhr.send(formData);
          document.getElementById("send-button").disabled = false;
    }




