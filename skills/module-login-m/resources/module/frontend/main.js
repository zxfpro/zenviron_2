const API_BASE = localStorage.getItem("LOGIN_M_API_BASE") || (window.location.protocol === "file:" ? "http://localhost:8000" : "/api");
const TOKEN_KEY = "login_m_access_token";

const views = {
  login: renderLogin,
  register: renderRegister,
  forgot: renderForgot,
  authed: renderAuthed,
};

let currentView = localStorage.getItem(TOKEN_KEY) ? "authed" : "login";
render();

function setMessage(msg = "") {
  document.getElementById("message").textContent = msg;
}

function go(view) {
  currentView = view;
  setMessage("");
  render();
}

function render() {
  views[currentView]();
}

function form(el) {
  return document.getElementById("auth-form").appendChild(el);
}

function resetContainers(title, sub) {
  document.getElementById("title").textContent = title;
  document.getElementById("subtitle").textContent = sub;
  document.getElementById("auth-form").innerHTML = "";
  document.getElementById("links").innerHTML = "";
}

function input(type, placeholder, name) {
  const el = document.createElement("input");
  el.type = type;
  el.placeholder = placeholder;
  el.name = name;
  return el;
}

function button(text, cls = "") {
  const el = document.createElement("button");
  el.type = "button";
  el.textContent = text;
  if (cls) el.className = cls;
  return el;
}

function link(text, onClick) {
  const a = document.createElement("a");
  a.textContent = text;
  a.onclick = onClick;
  return a;
}

async function api(path, method = "GET", body, auth = false) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await res.json();
  } catch (e) {}

  if (!res.ok) {
    throw new Error(data?.detail || "请求失败");
  }

  return data;
}

function renderLogin() {
  resetContainers("登录", "支持邮箱密码和手机验证码登录");
  const modeWrap = document.createElement("div");
  modeWrap.className = "mode-switch";
  const emailTab = document.createElement("button");
  emailTab.type = "button";
  emailTab.textContent = "邮箱登录";
  emailTab.className = "mode-btn active";
  const phoneTab = document.createElement("button");
  phoneTab.type = "button";
  phoneTab.textContent = "手机登录";
  phoneTab.className = "mode-btn";
  modeWrap.append(emailTab, phoneTab);
  form(modeWrap);

  let mode = "email";
  let timer = null;
  let leftSeconds = 0;

  const renderFields = () => {
    const container = document.getElementById("auth-form");
    container.querySelectorAll(".mode-dynamic").forEach((n) => n.remove());

    if (mode === "email") {
      const email = input("email", "邮箱", "email");
      email.className = "mode-dynamic";
      const pwd = input("password", "密码", "password");
      pwd.className = "mode-dynamic";
      const submit = button("登录");
      submit.className = "mode-dynamic";
      submit.onclick = async () => {
        try {
          const data = await api("/auth/login", "POST", { email: email.value, password: pwd.value });
          localStorage.setItem(TOKEN_KEY, data.access_token);
          go("authed");
        } catch (e) {
          setMessage(e.message);
        }
      };
      form(email);
      form(pwd);
      form(submit);
      return;
    }

    const phone = input("text", "手机号", "phone");
    phone.className = "mode-dynamic";

    const codeRow = document.createElement("div");
    codeRow.className = "code-row mode-dynamic";
    const code = input("text", "验证码", "code");
    const send = button(leftSeconds > 0 ? `${leftSeconds}s` : "发送验证码", "secondary");
    send.disabled = leftSeconds > 0;
    send.onclick = async () => {
      try {
        await api("/auth/phone/code", "POST", { phone: phone.value });
        setMessage("验证码已发送");
        leftSeconds = 60;
        if (timer) clearInterval(timer);
        timer = setInterval(() => {
          leftSeconds -= 1;
          renderFields();
          if (leftSeconds <= 0) {
            clearInterval(timer);
            timer = null;
          }
        }, 1000);
        renderFields();
      } catch (e) {
        setMessage(e.message);
      }
    };
    codeRow.append(code, send);

    const submit = button("手机登录");
    submit.className = "mode-dynamic";
    submit.onclick = async () => {
      try {
        const data = await api("/auth/phone/login", "POST", { phone: phone.value, code: code.value });
        localStorage.setItem(TOKEN_KEY, data.access_token);
        go("authed");
      } catch (e) {
        setMessage(e.message);
      }
    };
    form(phone);
    form(codeRow);
    form(submit);
  };

  emailTab.onclick = () => {
    mode = "email";
    emailTab.classList.add("active");
    phoneTab.classList.remove("active");
    renderFields();
  };
  phoneTab.onclick = () => {
    mode = "phone";
    phoneTab.classList.add("active");
    emailTab.classList.remove("active");
    renderFields();
  };
  renderFields();
  document.getElementById("links").append(link("注册", () => go("register")), link("忘记密码", () => go("forgot")));
}

function renderRegister() {
  resetContainers("注册", "邮箱验证码注册");
  const email = form(input("email", "邮箱", "email"));
  const code = form(input("text", "验证码", "code"));
  const pwd = form(input("password", "密码（至少8位）", "password"));
  const confirm = form(input("password", "确认密码", "confirm"));
  const send = form(button("发送验证码", "secondary"));
  const submit = form(button("提交注册"));

  send.onclick = async () => {
    try {
      await api("/auth/register/email/code", "POST", { email: email.value });
      setMessage("验证码已发送");
    } catch (e) {
      setMessage(e.message);
    }
  };

  submit.onclick = async () => {
    if (pwd.value !== confirm.value) {
      setMessage("两次密码不一致");
      return;
    }
    try {
      await api("/auth/register_with_code", "POST", { email: email.value, code: code.value, password: pwd.value });
      setMessage("注册成功，请登录");
      go("login");
    } catch (e) {
      setMessage(e.message);
    }
  };

  document.getElementById("links").append(link("返回登录", () => go("login")));
}

function renderForgot() {
  resetContainers("忘记密码", "邮箱验证码重置密码");
  const email = form(input("email", "邮箱", "email"));
  const code = form(input("text", "验证码", "code"));
  const pwd = form(input("password", "新密码", "password"));
  const send = form(button("发送验证码", "secondary"));
  const submit = form(button("提交重置"));

  send.onclick = async () => {
    try {
      await api("/auth/password/forgot", "POST", { email: email.value });
      setMessage("验证码已发送");
    } catch (e) {
      setMessage(e.message);
    }
  };

  submit.onclick = async () => {
    try {
      await api("/auth/password/reset", "POST", { email: email.value, code: code.value, new_password: pwd.value });
      setMessage("重置成功，请登录");
      go("login");
    } catch (e) {
      setMessage(e.message);
    }
  };

  document.getElementById("links").append(link("返回登录", () => go("login")));
}

async function renderAuthed() {
  resetContainers("已登录", "当前会话信息");
  const info = document.createElement("pre");
  info.style.background = "#f8fafc";
  info.style.padding = "12px";
  info.style.borderRadius = "8px";
  form(info);
  const logoutBtn = form(button("退出登录", "secondary"));

  try {
    const me = await api("/auth/me", "GET", undefined, true);
    info.textContent = JSON.stringify(me, null, 2);
  } catch (e) {
    setMessage(e.message || "会话失效");
    localStorage.removeItem(TOKEN_KEY);
    go("login");
    return;
  }

  logoutBtn.onclick = () => {
    localStorage.removeItem(TOKEN_KEY);
    go("login");
  };
}
