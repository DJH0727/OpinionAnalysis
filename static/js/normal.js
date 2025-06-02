    //判断文件类型
function getFileCategory(file) {
  const fileType = file.type;
  const fileName = file.name.toLowerCase();

  if (fileType.includes("pdf") || fileName.endsWith(".pdf")) {
    return "pdf";
  } else if (
    fileType === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
    fileType === "application/vnd.ms-excel" ||
    fileName.endsWith(".xls") || fileName.endsWith(".xlsx")
  ) {
    return "excel";
  } else if (
    fileType === "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
    fileType === "application/msword" ||
    fileName.endsWith(".doc") || fileName.endsWith(".docx")
  ) {
    return "word";
  } else if (fileType.startsWith("image/")) {
    return "image";
  } else if (fileType === "text/plain" || fileName.endsWith(".txt")) {
    return "txt";
  } else {
    return "unknown";
  }
}
function getFileCategoryByName (fileName) {
  const fileType = fileName.split(".").pop();

  if (fileType === "pdf") {
    return "pdf";
  } else if (fileType === "xls" || fileType === "xlsx") {
    return "excel";
  } else if (fileType === "doc" || fileType === "docx") {
    return "word";
  } else if (fileType === "jpg" || fileType === "jpeg" || fileType === "png" || fileType === "gif") {
    return "image";
  } else if (fileType === "txt") {
    return "txt";
  } else {
    return "unknown";
  }
}



    // 主题切换
function toggleTheme() {
   const body = document.body;
   const currentTheme = body.getAttribute("data-theme");
   const newTheme = currentTheme === "dark" ? "light" : "dark";
   body.setAttribute("data-theme", newTheme);
}