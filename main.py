import os
import pandas as pd
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Configurar tamaño máximo de archivos subidos (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

HTML_CONTENT = r"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Control de Gastos Personales</title>

  <style>
    :root {
      --bg-main: #F1F5F9;
      --bg-card: #FFFFFF;
      --primary-navy: #1E40AF;
      --primary-hover: #1D4ED8;
      --accent-green: #16A34A;
      --accent-red: #DC2626;
      --text-main: #0F172A;
      --text-muted: #64748B;
      --border-color: #CBD5E1;
      --font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: var(--bg-main);
      color: var(--text-main);
      font-family: var(--font-family);
      min-height: 100vh;
      padding: 1.5rem;
      line-height: 1.5;
    }

    .welcome-wrapper {
      min-height: calc(100vh - 3rem);
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .welcome-container {
      width: 100%;
      max-width: 850px;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 24px;
      padding: 4.5rem 4rem;
      box-shadow: 0 25px 30px -5px rgba(0,0,0,0.07);
      text-align: center;
    }

    .welcome-title {
      font-size: 3rem;
      color: var(--primary-navy);
      font-weight: 800;
      margin-bottom: 0.75rem;
    }

    .welcome-subtitle {
      color: var(--text-muted);
      font-size: 1.25rem;
      margin-bottom: 3.5rem;
    }

    .form-user {
      display: flex;
      flex-direction: column;
      gap: 2rem;
      text-align: left;
    }

    .form-user label {
      font-weight: 700;
      font-size: 1.2rem;
      color: var(--text-main);
    }

    .form-user input {
      width: 100%;
      padding: 1.3rem 1.4rem;
      border: 2px solid var(--border-color);
      border-radius: 14px;
      font-size: 1.25rem;
      outline: none;
    }

    .form-user input:focus { border-color: var(--primary-navy); }

    .btn-stack {
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      margin-top: 1rem;
    }

    .btn {
      padding: 1.1rem 1.8rem;
      border-radius: 14px;
      font-weight: 600;
      font-size: 1.1rem;
      cursor: pointer;
      border: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.75rem;
      transition: all 0.2s ease;
      text-decoration: none;
    }

    .btn-navy { background-color: var(--primary-navy); color: #ffffff; }
    .btn-navy:hover { background-color: var(--primary-hover); }

    .btn-outline {
      background-color: #FFFFFF;
      border: 2px solid var(--border-color);
      color: var(--text-main);
    }
    .btn-outline:hover { background-color: #F8FAFC; border-color: #94A3B8; }

    .main-app {
      display: none;
      width: 100%;
      flex-direction: column;
      gap: 1.5rem;
    }

    .header-top {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 18px;
      padding: 1.25rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
    }

    .header-user-info { display: flex; align-items: center; gap: 1rem; }

    .user-badge {
      background-color: #EFF6FF;
      color: var(--primary-navy);
      padding: 0.5rem 1rem;
      border-radius: 12px;
      font-weight: 800;
      font-size: 1.4rem;
      border: 1px solid #BFDBFE;
    }

    .header-title-text h1 { font-size: 1.8rem; color: var(--primary-navy); font-weight: 800; }
    .header-title-text p { color: var(--text-muted); font-size: 1rem; }

    .summary-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.5rem;
    }

    .stat-card {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 1.75rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .stat-card.balance { border-left: 6px solid var(--primary-navy); }
    .stat-card.ingresos { border-left: 6px solid var(--accent-green); }
    .stat-card.gastos { border-left: 6px solid var(--accent-red); }

    .stat-header { display: flex; justify-content: space-between; align-items: center; }

    .stat-title {
      font-size: 0.95rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-muted);
      font-weight: 700;
    }

    .stat-value { font-size: 2.5rem; font-weight: 800; margin-top: 0.5rem; color: var(--text-main); }

    .edit-btn {
      background: none;
      border: none;
      cursor: pointer;
      font-size: 1rem;
      color: var(--text-muted);
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
    }
    .edit-btn:hover { background-color: #F1F5F9; color: var(--primary-navy); }

    .input-ingreso {
      font-size: 1.8rem;
      font-weight: 800;
      width: 100%;
      padding: 0.4rem 0.6rem;
      border: 2px solid var(--primary-navy);
      border-radius: 8px;
      margin-top: 0.5rem;
    }

    .panel-box {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 18px;
      padding: 2rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
      flex-grow: 1;
    }

    .panel-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
    .panel-title { font-size: 1.5rem; font-weight: 700; color: var(--primary-navy); }

    .gastos-list-table { width: 100%; border-collapse: collapse; }
    .gastos-list-table th, .gastos-list-table td {
      padding: 1.2rem 1.4rem;
      text-align: left;
      border-bottom: 1px solid var(--border-color);
      font-size: 1.1rem;
    }
    .gastos-list-table th { background-color: #F8FAFC; color: var(--text-muted); font-weight: 700; }

    .excel-standalone-view {
      display: none;
      width: 100%;
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-top: 6px solid var(--primary-navy);
      border-radius: 16px;
      padding: 2.25rem;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
    }

    .excel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid var(--border-color);
    }

    .table-wrapper { overflow-x: auto; max-height: 70vh; overflow-y: auto; }

    .excel-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 1.1rem; }
    .excel-table th {
      background-color: #F1F5F9;
      color: var(--primary-navy);
      font-weight: 700;
      padding: 1.2rem 1.4rem;
      border-bottom: 2px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 10;
    }
    .excel-table td { padding: 1rem 1.4rem; border-bottom: 1px solid var(--border-color); }
    .excel-table tr:hover { background-color: #F8FAFC; }

    .modal-overlay {
      display: none;
      position: fixed;
      top: 0; left: 0;
      width: 100vw; height: 100vh;
      background: rgba(15, 23, 42, 0.65);
      justify-content: center;
      align-items: center;
      z-index: 9999;
    }

    .modal-content {
      background: var(--bg-card);
      border-radius: 20px;
      padding: 3.5rem;
      width: 90%;
      max-width: 720px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.3);
    }

    .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
    .form-group { margin-bottom: 1.75rem; }
    .form-group label { display: block; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.75rem; color: var(--text-main); }
    .form-control { width: 100%; padding: 1.2rem 1.3rem; border: 2px solid var(--border-color); border-radius: 12px; font-size: 1.15rem; outline: none; }
    .form-control:focus { border-color: var(--primary-navy); }

    .empty-msg { color: var(--text-muted); text-align: center; padding: 4rem 2rem; font-style: italic; font-size: 1.2rem; }
  </style>
</head>
<body>

  <!-- PANTALLA DE AUTENTICACIÓN -->
  <div class="welcome-wrapper" id="vista-auth">
    <div class="welcome-container">
      <h1 class="welcome-title" id="auth-titulo">Iniciar Sesión</h1>
      <p class="welcome-subtitle" id="auth-subtitulo">Ingresa tus datos para continuar</p>

      <form class="form-user" onsubmit="procesarAuth(event)">
        <div>
          <label for="auth-email">Correo Electrónico</label>
          <input type="email" id="auth-email" placeholder="usuario@ejemplo.com" required autocomplete="off">
        </div>
        <div>
          <label for="auth-pass">Contraseña</label>
          <input type="password" id="auth-pass" placeholder="••••••••" required autocomplete="off">
        </div>

        <div class="btn-stack">
          <button type="submit" class="btn btn-navy" id="auth-btn-submit">Entrar</button>
          <button type="button" class="btn btn-outline" onclick="alternarModoAuth()">
            <span id="auth-toggle-msg">¿No tienes cuenta? Regístrate aquí</span>
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- PANTALLA DE SELECCIÓN -->
  <div class="welcome-wrapper" id="vista-inicio" style="display: none;">
    <div class="welcome-container">
      <h1 class="welcome-title">Gestión de Gastos</h1>
      <p class="welcome-subtitle">Selecciona una opción para comenzar</p>

      <div class="form-user">
        <div>
          <label for="nombre-usuario">1. Nombre de la persona</label>
          <input type="text" id="nombre-usuario" placeholder="Ej: Joaquín" style="margin-top: 0.75rem;" autocomplete="off">
        </div>

        <div class="btn-stack">
          <button class="btn btn-navy" onclick="irAArchivosPersona()">
            📂 2. Ir a datos / gastos de la persona
          </button>

          <input type="file" id="input-excel" accept=".xlsx, .xls, .csv" style="display: none;" onchange="subirExcelWeb(this)">
          <button class="btn btn-outline" onclick="document.getElementById('input-excel').click()">
            📊 3. Importar Excel (Independiente)
          </button>

          <button class="btn btn-outline" style="color: var(--accent-red);" onclick="cerrarSesion()">
            🚪 Cerrar Sesión
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- PANEL PRINCIPAL -->
  <div class="main-app" id="vista-panel">
    <header class="header-top">
      <div class="header-user-info">
        <span class="user-badge" id="badge-usuario">Persona</span>
        <div class="header-title-text">
          <h1 id="titulo-panel">Gestión de Gastos</h1>
          <p id="subtitulo-panel">Panel de administración asignado</p>
        </div>
      </div>
      
      <div style="display: flex; gap: 1rem;">
        <button class="btn btn-outline" onclick="volverAInicio()">
          🏠 Volver al Inicio
        </button>
        <button class="btn btn-navy" onclick="abrirModalGasto()">+ Registrar Gasto</button>
      </div>
    </header>

    <section class="summary-grid">
      <div class="stat-card balance">
        <div class="stat-header">
          <span class="stat-title">Balance Disponible</span>
        </div>
        <div class="stat-value" id="val-balance">$0,00</div>
      </div>

      <div class="stat-card ingresos">
        <div class="stat-header">
          <span class="stat-title">Ingresos Mensuales</span>
          <button class="edit-btn" onclick="habilitarEdicionIngreso()" title="Editar ingreso">✏️ Modificar</button>
        </div>
        <div id="box-ingreso-view">
          <div class="stat-value" id="val-ingresos" style="color: var(--accent-green);">$0,00</div>
        </div>
        <div id="box-ingreso-edit" style="display: none;">
          <input type="text" id="input-ingreso-val" class="input-ingreso" placeholder="Ej: 1.500.000 o 1500">
          <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem; justify-content: flex-end;">
            <button class="btn btn-navy" style="padding: 0.5rem 1rem; font-size: 0.95rem;" onclick="guardarIngreso()">Guardar</button>
          </div>
        </div>
      </div>

      <div class="stat-card gastos">
        <div class="stat-header">
          <span class="stat-title">Gastos del Mes</span>
        </div>
        <div class="stat-value" id="val-gastos" style="color: var(--accent-red);">$0,00</div>
      </div>
    </section>

    <section class="panel-box">
      <div class="panel-header-row">
        <div class="panel-title">Historial de Gastos Registrados</div>
        <button class="btn btn-navy" style="padding: 0.6rem 1.2rem; font-size: 1rem;" onclick="abrirModalGasto()">+ Añadir Gasto</button>
      </div>

      <div id="contenedor-gastos">
        <div class="empty-msg" id="msg-vacio">Aún no has registrado ningún gasto este mes. Haz clic en <strong>"+ Registrar Gasto"</strong> para añadir uno.</div>
        <table class="gastos-list-table" id="tabla-gastos-historial" style="display: none;">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Concepto / Descripción</th>
              <th>Monto</th>
            </tr>
          </thead>
          <tbody id="tbody-gastos">
          </tbody>
        </table>
      </div>
    </section>
  </div>

  <div id="vista-excel-standalone" class="excel-standalone-view">
    <div class="excel-header">
      <div>
        <strong id="archivo-nombre" style="color: var(--primary-navy); font-size: 1.5rem;">Documento Importado</strong>
        <p style="font-size: 1rem; color: var(--text-muted);">Vista previa independiente de archivo Excel / CSV</p>
      </div>
      <button class="btn btn-outline" style="font-size: 1rem;" onclick="cerrarVistaExcelStandalone()">🏠 Volver al Inicio</button>
    </div>

    <div class="table-wrapper" id="tabla-wrapper-standalone">
    </div>
  </div>

  <div class="modal-overlay" id="modal-gasto">
    <div class="modal-content">
      <div class="modal-header">
        <h3 style="color: var(--primary-navy); font-size: 1.8rem; font-weight: 700;">Nuevo Gasto</h3>
        <button class="btn btn-outline" style="padding: 0.5rem 1rem; font-size: 1.2rem;" onclick="cerrarModalGasto()">✕</button>
      </div>
      <form onsubmit="guardarGasto(event)">
        <div class="form-group">
          <label>Concepto / Descripción</label>
          <input type="text" id="gasto-concepto" class="form-control" placeholder="Ej: Supermercado" required autocomplete="off">
        </div>
        <div class="form-group">
          <label>Monto ($) <span style="font-size: 0.9rem; font-weight: normal; color: var(--text-muted);">(Ej: 1500, 1.500, 1500,50)</span></label>
          <input type="text" id="gasto-monto" class="form-control" placeholder="0.00" required autocomplete="off">
        </div>
        <div class="form-group">
          <label>Fecha</label>
          <input type="date" id="gasto-fecha" class="form-control" required>
        </div>
        <div style="display: flex; gap: 1rem; justify-content: flex-end; margin-top: 2.5rem;">
          <button type="button" class="btn btn-outline" onclick="cerrarModalGasto()">Cancelar</button>
          <button type="submit" class="btn btn-navy" style="font-size: 1.1rem; padding: 1.1rem 2.2rem;">Guardar Gasto</button>
        </div>
      </form>
    </div>
  </div>

  <script>
    let modoRegistro = false;
    let usuarioActual = null;
    let nombreUsuarioClave = '';
    let datosUsuario = { ingresos: 0, gastos: 0, listaGastos: [] };

    function alternarModoAuth() {
      modoRegistro = !modoRegistro;
      document.getElementById('auth-titulo').innerText = modoRegistro ? 'Crear Cuenta' : 'Iniciar Sesión';
      document.getElementById('auth-subtitulo').innerText = modoRegistro ? 'Registra una nueva cuenta' : 'Ingresa tus datos para continuar';
      document.getElementById('auth-btn-submit').innerText = modoRegistro ? 'Registrarse' : 'Entrar';
      document.getElementById('auth-toggle-msg').innerText = modoRegistro ? '¿Ya tienes cuenta? Inicia sesión' : '¿No tienes cuenta? Regístrate aquí';
    }

    function procesarAuth(e) {
      e.preventDefault();
      const email = document.getElementById('auth-email').value.trim().toLowerCase();
      const pass = document.getElementById('auth-pass').value;
      let usuarios = JSON.parse(localStorage.getItem('usuarios_app') || '{}');

      if (modoRegistro) {
        if (usuarios[email]) {
          alert('El correo ya está registrado.');
          return;
        }
        usuarios[email] = { password: pass, ingresos: 0, gastos: 0, listaGastos: [] };
        localStorage.setItem('usuarios_app', JSON.stringify(usuarios));
        alert('Cuenta creada exitosamente. Ahora puedes iniciar sesión.');
        alternarModoAuth();
      } else {
        if (!usuarios[email] || usuarios[email].password !== pass) {
          alert('Correo o contraseña incorrectos.');
          return;
        }
        usuarioActual = email;
        localStorage.setItem('sesion_activa', email);
        cargarPanelUsuario();
      }
    }

    function cargarPanelUsuario() {
      document.getElementById('vista-auth').style.display = 'none';
      document.getElementById('vista-inicio').style.display = 'flex';
    }

    window.addEventListener('DOMContentLoaded', () => {
      const sesionGuardada = localStorage.getItem('sesion_activa');
      if (sesionGuardada) {
        usuarioActual = sesionGuardada;
        cargarPanelUsuario();
      }
    });

    function cerrarSesion() {
      localStorage.removeItem('sesion_activa');
      location.reload();
    }

    function parsearMontoFlexible(montoStr) {
      if (typeof montoStr === 'number') return montoStr;
      if (!montoStr) return 0;
      let str = montoStr.toString().trim();
      if (str.includes('.') && str.includes(',')) {
        str = str.replace(/\./g, '').replace(',', '.');
      } else if (str.includes('.')) {
        const partes = str.split('.');
        if (partes.length > 2 || partes[partes.length - 1].length === 3) {
          str = str.replace(/\./g, '');
        }
      } else if (str.includes(',')) {
        str = str.replace(',', '.');
      }
      const num = parseFloat(str);
      return isNaN(num) ? 0 : num;
    }

    function formatearMoneda(monto) {
      return '$' + monto.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function cargarDatosUsuario() {
      try {
        const datosGuardados = localStorage.getItem('usuario_gastos_' + nombreUsuarioClave);
        datosUsuario = datosGuardados ? JSON.parse(datosGuardados) : { ingresos: 0, gastos: 0, listaGastos: [] };
      } catch (e) {
        datosUsuario = { ingresos: 0, gastos: 0, listaGastos: [] };
      }
      actualizarPantallaPanel();
    }

    function guardarDatosUsuario() {
      if (nombreUsuarioClave) {
        try {
          localStorage.setItem('usuario_gastos_' + nombreUsuarioClave, JSON.stringify(datosUsuario));
        } catch (e) {}
      }
    }

    function irAArchivosPersona() {
      const inputNom = document.getElementById('nombre-usuario').value.trim();
      if (!inputNom) {
        alert('Por favor, ingresa el nombre de la persona para continuar.');
        return;
      }
      nombreUsuarioClave = inputNom.toLowerCase();
      document.getElementById('badge-usuario').innerText = inputNom;
      document.getElementById('titulo-panel').innerText = `Gestión de Gastos`;
      document.getElementById('subtitulo-panel').innerText = `Control y registro de ingresos/gastos`;
      cargarDatosUsuario();

      document.getElementById('vista-inicio').style.display = 'none';
      document.getElementById('vista-excel-standalone').style.display = 'none';
      document.getElementById('vista-panel').style.display = 'flex';
    }

    function volverAInicio() {
      document.getElementById('vista-panel').style.display = 'none';
      document.getElementById('vista-excel-standalone').style.display = 'none';
      document.getElementById('vista-inicio').style.display = 'flex';
    }

    function actualizarPantallaPanel() {
      document.getElementById('val-ingresos').innerText = formatearMoneda(datosUsuario.ingresos);
      document.getElementById('val-gastos').innerText = formatearMoneda(datosUsuario.gastos);
      const balance = datosUsuario.ingresos - datosUsuario.gastos;
      const valBalanceElem = document.getElementById('val-balance');
      valBalanceElem.innerText = formatearMoneda(balance);
      valBalanceElem.style.color = balance < 0 ? 'var(--accent-red)' : 'var(--text-main)';
      actualizarTablaHistorial();
    }

    function habilitarEdicionIngreso() {
      document.getElementById('box-ingreso-view').style.display = 'none';
      document.getElementById('box-ingreso-edit').style.display = 'block';
      document.getElementById('input-ingreso-val').value = datosUsuario.ingresos || '';
    }

    function guardarIngreso() {
      const inputValRaw = document.getElementById('input-ingreso-val').value;
      datosUsuario.ingresos = parsearMontoFlexible(inputValRaw);
      guardarDatosUsuario();
      actualizarPantallaPanel();
      document.getElementById('box-ingreso-edit').style.display = 'none';
      document.getElementById('box-ingreso-view').style.display = 'block';
    }

    function abrirModalGasto() {
      document.getElementById('modal-gasto').style.display = 'flex';
      const fechaInput = document.getElementById('gasto-fecha');
      if (!fechaInput.value) fechaInput.valueAsDate = new Date();
    }

    function cerrarModalGasto() {
      document.getElementById('modal-gasto').style.display = 'none';
    }

    function guardarGasto(e) {
      e.preventDefault();
      const concepto = document.getElementById('gasto-concepto').value;
      const montoRaw = document.getElementById('gasto-monto').value;
      const fecha = document.getElementById('gasto-fecha').value;
      const montoParsed = parsearMontoFlexible(montoRaw);

      datosUsuario.gastos += montoParsed;
      datosUsuario.listaGastos.unshift({ concepto, monto: montoParsed, fecha });
      guardarDatosUsuario();
      actualizarPantallaPanel();

      document.getElementById('gasto-concepto').value = '';
      document.getElementById('gasto-monto').value = '';
      cerrarModalGasto();
    }

    function actualizarTablaHistorial() {
      if (datosUsuario.listaGastos.length === 0) {
        document.getElementById('msg-vacio').style.display = 'block';
        document.getElementById('tabla-gastos-historial').style.display = 'none';
        return;
      }
      document.getElementById('msg-vacio').style.display = 'none';
      document.getElementById('tabla-gastos-historial').style.display = 'table';
      const tbody = document.getElementById('tbody-gastos');
      tbody.innerHTML = '';
      datosUsuario.listaGastos.forEach(gasto => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${gasto.fecha}</td>
          <td><strong>${gasto.concepto}</strong></td>
          <td style="color: var(--accent-red); font-weight: 700;">-${formatearMoneda(gasto.monto)}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    function subirExcelWeb(input) {
      if (!input.files || !input.files[0]) return;

      const file = input.files[0];
      const formData = new FormData();
      formData.append('file', file);

      fetch('/importar-excel', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          alert('Error: ' + data.error);
        } else {
          mostrarTablaExcelStandalone(data.html, data.filename);
        }
      })
      .catch(err => alert('Error procesando archivo: ' + err));
    }

    function mostrarTablaExcelStandalone(htmlTabla, nombreArchivo) {
      document.getElementById('vista-inicio').style.display = 'none';
      document.getElementById('vista-panel').style.display = 'none';
      document.getElementById('archivo-nombre').innerText = `Documento: ${nombreArchivo}`;
      document.getElementById('tabla-wrapper-standalone').innerHTML = htmlTabla;
      document.getElementById('vista-excel-standalone').style.display = 'block';
    }

    function cerrarVistaExcelStandalone() {
      document.getElementById('vista-excel-standalone').style.display = 'none';
      document.getElementById('vista-inicio').style.display = 'flex';
    }
  </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CONTENT)

@app.route('/importar-excel', methods=['POST'])
def importar_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        df = df.fillna('')
        tabla_html = df.to_html(classes="excel-table", index=False, escape=False)
        return jsonify({'html': tabla_html, 'filename': file.filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)