import os
import pandas as pd
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

HTML_CONTENT = r"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Control Financiero - Plantilla Mensual</title>
  <link href="https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap" rel="stylesheet">

  <style>
    :root {
      --excel-header: #217346;
      --excel-border: #d4d4d4;
      --excel-bg-head: #f3f2f1;
      --excel-hover: #e1dfdd;
      --text-main: #323130;
      --accent-red: #a80000;
      --accent-green: #107c41;
      --accent-blue: #0078d4;
      --primary-navy: #1E40AF;
      --border-color: #E2E8F0;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f8f9fa;
      color: var(--text-main);
      height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* AUTENTICACIÓN Y SELECCIÓN DE USUARIO */
    .welcome-wrapper {
      min-height: calc(100vh - 2rem);
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 1rem;
    }

    .welcome-container {
      width: 100%;
      max-width: 450px;
      background: #ffffff;
      border: 1px solid var(--excel-border);
      border-radius: 8px;
      padding: 2.5rem 2rem;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      border-top: 4px solid var(--excel-header);
      text-align: center;
    }

    .welcome-title { font-size: 1.8rem; color: var(--excel-header); font-weight: 700; margin-bottom: 0.5rem; }
    .welcome-subtitle { color: #605e5c; font-size: 0.95rem; margin-bottom: 2rem; }

    .form-user { display: flex; flex-direction: column; gap: 1.2rem; text-align: left; }
    .form-user label { font-weight: 600; font-size: 0.9rem; color: var(--text-main); }
    .form-user input { width: 100%; padding: 0.6rem 0.8rem; border: 1px solid var(--excel-border); border-radius: 4px; font-size: 0.95rem; outline: none; }
    .form-user input:focus { border-color: var(--excel-header); }

    .btn-stack { display: flex; flex-direction: column; gap: 0.8rem; margin-top: 0.5rem; }

    .btn {
      padding: 0.5rem 1rem;
      border-radius: 4px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid transparent;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.4rem;
      transition: all 0.2s ease;
      text-decoration: none;
    }

    .btn-excel { background: var(--excel-header); color: white; }
    .btn-excel:hover { background: #1e6b40; }

    .btn-navy { background-color: var(--primary-navy); color: #ffffff; }
    .btn-navy:hover { background-color: #1d4ed8; }

    .btn-outline { background: white; border-color: #8a8886; color: var(--text-main); }
    .btn-outline:hover { background: #f3f2f1; }

    /* BARRA SUPERIOR COMPACTA */
    .top-bar {
      background: #ffffff;
      border-bottom: 2px solid var(--excel-header);
      padding: 0.5rem 1.2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .brand-section { display: flex; align-items: center; gap: 0.8rem; }
    .brand-title { font-weight: 700; font-size: 1.1rem; color: var(--excel-header); white-space: nowrap; }

    .month-picker-container {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      background: #f3f2f1;
      border: 1px solid var(--excel-border);
      padding: 0.25rem 0.6rem;
      border-radius: 4px;
    }

    .month-picker-label { font-size: 0.8rem; font-weight: 600; color: #605e5c; }

    .month-picker-input {
      border: 1px solid #c8c6c4;
      background: #ffffff;
      border-radius: 3px;
      padding: 0.2rem 0.4rem;
      font-family: inherit;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-main);
      outline: none;
      cursor: pointer;
    }

    .month-picker-input:focus { border-color: var(--excel-header); }

    .top-actions { display: flex; gap: 0.5rem; align-items: center; }

    /* CONTENEDOR DE LA PLANTILLA */
    .main-app { display: none; height: 100vh; flex-direction: column; }

    .sheet-container {
      flex: 1;
      padding: 0.8rem;
      display: flex;
      flex-direction: column;
      gap: 0.8rem;
      overflow: hidden;
    }

    .table-wrapper {
      flex: 1;
      background: white;
      border: 1px solid var(--excel-border);
      overflow: auto;
      position: relative;
    }

    .excel-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      user-select: none;
    }

    .excel-table th {
      background: var(--excel-bg-head);
      color: #323130;
      font-weight: 600;
      border: 1px solid var(--excel-border);
      padding: 0.4rem 0.6rem;
      text-align: left;
      position: sticky;
      top: 0;
      z-index: 10;
      cursor: grab;
    }

    .excel-table th:active { cursor: grabbing; }

    .excel-table td {
      border: 1px solid var(--excel-border);
      padding: 0.35rem 0.6rem;
      white-space: nowrap;
    }

    .excel-table tr:hover { background-color: #f8f8f8; }

    .cell-input {
      width: 100%;
      border: none;
      outline: none;
      background: transparent;
      font-family: inherit;
      font-size: inherit;
      color: inherit;
    }

    .cell-input:disabled {
      background-color: #f3f2f1;
      color: #a19f9d;
      cursor: not-allowed;
      text-align: center;
    }

    .cell-input:focus:not(:disabled) {
      background: white;
      box-shadow: inset 0 0 0 2px var(--excel-header);
    }

    .cuota-container {
      display: flex;
      gap: 0.3rem;
      align-items: center;
    }

    .select-cuotas-type {
      border: 1px solid #c8c6c4;
      border-radius: 3px;
      font-size: 0.75rem;
      padding: 0.1rem 0.2rem;
      background: #fff;
      cursor: pointer;
    }

    .select-status {
      width: 100%;
      border: none;
      outline: none;
      background: transparent;
      font-family: inherit;
      font-size: 0.78rem;
      font-weight: 700;
      padding: 0.2rem 0.4rem;
      border-radius: 3px;
      cursor: pointer;
      text-align-last: center;
    }

    .status-pagado { background: #dfd; color: #107c41; }
    .status-pendiente { background: #fff4ce; color: #797000; }
    .status-vencido { background: #fde8e8; color: #a80000; }
    .status-cuotas { background: #e1dfdd; color: #323130; }

    .col-drag-handle { margin-right: 0.3rem; color: #a19f9d; }

    /* SECCIÓN INFERIOR DE TOTALES Y AHORRO */
    .summary-footer {
      background: #ffffff;
      border: 1px solid var(--excel-border);
      border-top: 3px solid var(--excel-header);
      padding: 0.8rem 1.2rem;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1rem;
      border-radius: 4px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }

    .summary-card {
      background: #f8f9fa;
      border: 1px solid #e1dfdd;
      padding: 0.6rem 0.9rem;
      border-radius: 6px;
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
    }

    .summary-card.highlight {
      background: #f0fdf4;
      border-color: #b7eb8f;
    }

    .summary-card.negative {
      background: #fff1f0;
      border-color: #ffa39e;
    }

    .summary-title {
      font-size: 0.75rem;
      font-weight: 700;
      color: #605e5c;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .summary-input {
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--accent-green);
      border: 1px dashed #a19f9d;
      background: #fff;
      padding: 0.2rem 0.4rem;
      border-radius: 4px;
      outline: none;
      width: 100%;
    }

    .summary-value {
      font-size: 1.25rem;
      font-weight: 700;
    }

    .excel-standalone-view {
      display: none; width: 100%; background-color: #ffffff;
      border: 1px solid var(--excel-border); border-radius: 8px; padding: 2rem;
    }
  </style>
</head>
<body>

  <!-- AUTENTICACIÓN -->
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

  <!-- SELECCIÓN DE PERSONA -->
  <div class="welcome-wrapper" id="vista-inicio" style="display: none;">
    <div class="welcome-container">
      <h1 class="welcome-title">Gestión de Gastos</h1>
      <p class="welcome-subtitle">Selecciona una opción para comenzar (<span id="user-display-email" style="color: var(--primary-navy); font-weight: bold;"></span>)</p>

      <div class="form-user">
        <div>
          <label for="nombre-usuario">1. Nombre de la persona</label>
          <input type="text" id="nombre-usuario" placeholder="Ej: Joaquín" autocomplete="off">
        </div>

        <div class="btn-stack">
          <button class="btn btn-excel" onclick="irAArchivosPersona()">📁 2. Ir a la Plantilla de Gastos</button>
          <input type="file" id="input-excel" accept=".xlsx, .xls, .csv" style="display: none;" onchange="subirExcelWeb(this)">
          <button class="btn btn-outline" onclick="document.getElementById('input-excel').click()">📊 Importar Excel Externo</button>
          <button class="btn btn-outline" style="color: var(--accent-red);" onclick="cerrarSesion()">🚪 Cerrar Sesión</button>
        </div>
      </div>
    </div>
  </div>

  <datalist id="categorias-list">
    <option value="Servicios"></option>
    <option value="Tarjetas"></option>
    <option value="Alquiler"></option>
    <option value="Comida"></option>
    <option value="Suscripciones"></option>
  </datalist>

  <!-- PANTALLA PRINCIPAL: PLANTILLA MENSUAL -->
  <div class="main-app" id="vista-panel">
    <header class="top-bar">
      <div class="brand-section">
        <span class="brand-title">📊 Control Mensual</span>
        <span id="user-display" style="font-size: 0.8rem; background: #e1dfdd; padding: 0.2rem 0.5rem; border-radius: 12px; font-weight: 600;">Usuario</span>
        <span id="badge-email-header" style="font-size: 0.8rem; background: #eff6ff; color: var(--primary-navy); padding: 0.2rem 0.5rem; border-radius: 12px; font-weight: 600; border: 1px solid #bfdbfe;">email</span>

        <div class="month-picker-container">
          <span class="month-picker-label">📅 Mes:</span>
          <input type="month" id="selected-month" class="month-picker-input" value="2026-08" onchange="cargarDatosUsuario()">
        </div>
      </div>

      <div class="top-actions">
        <button class="btn btn-outline" onclick="renovarMes()">🔄 Clonar Mes a Siguiente</button>
        <button class="btn btn-excel" onclick="agregarFila()">+ Nueva Fila</button>
        <button class="btn btn-outline" onclick="volverAInicio()">🗙 Menú</button>
      </div>
    </header>

    <main class="sheet-container">
      <div class="table-wrapper">
        <table class="excel-table" id="finance-table">
          <thead>
            <tr>
              <th draggable="true"><span class="col-drag-handle">⋮⋮</span>Fecha Venc.</th>
              <th draggable="true"><span class="col-drag-handle">⋮⋮</span>Categoría</th>
              <th draggable="true"><span class="col-drag-handle">⋮⋮</span>Concepto / Detalle</th>
              <th draggable="true"><span class="col-drag-handle">⋮⋮</span>Modo / Cuotas</th>
              <th draggable="true"><span class="col-drag-handle">⋮⋮</span>Fin de Pago</th>
              <th draggable="true" style="text-align: right;"><span class="col-drag-handle">⋮⋮</span>Monto ($)</th>
              <th draggable="true" style="text-align: center;"><span class="col-drag-handle">⋮⋮</span>Estado (Fijar)</th>
              <th style="width: 40px; text-align: center;">⚙️</th>
            </tr>
          </thead>
          <tbody id="table-body">
            <!-- Carga dinámica -->
          </tbody>
        </table>
      </div>

      <footer class="summary-footer">
        <div class="summary-card">
          <span class="summary-title">💵 Ingresos del Mes</span>
          <input type="text" id="ingresos-input" class="summary-input" value="0,00" oninput="marcarIngresoModificado()">
        </div>

        <div class="summary-card">
          <span class="summary-title">📉 Total Gastos</span>
          <span id="total-gastos-val" class="summary-value" style="color: var(--accent-red);">$0,00</span>
        </div>

        <div class="summary-card highlight" id="ahorro-card">
          <span class="summary-title">💰 Disponible para Ahorro</span>
          <span id="total-ahorro-val" class="summary-value" style="color: var(--accent-green);">$0,00</span>
        </div>
      </footer>
    </main>
  </div>

  <!-- VISTA EXCEL STANDALONE -->
  <div id="vista-excel-standalone" class="excel-standalone-view">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
      <strong id="archivo-nombre" style="color: var(--primary-navy); font-size: 1.5rem;">Documento Importado</strong>
      <button class="btn btn-outline" onclick="cerrarVistaExcelStandalone()">🏠 Volver al Inicio</button>
    </div>
    <div id="tabla-wrapper-standalone" class="table-wrapper"></div>
  </div>

  <script>
    let modoRegistro = false;
    let usuarioActual = null;
    let nombreUsuarioClave = '';
    let datosUsuario = { ingresos: "0,00", filas: [] };

    // AUTENTICACIÓN
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
        if (usuarios[email]) return alert('El correo ya está registrado.');
        usuarios[email] = { password: pass };
        localStorage.setItem('usuarios_app', JSON.stringify(usuarios));
        alert('Cuenta creada exitosamente. Inicia sesión ahora.');
        alternarModoAuth();
      } else {
        if (!usuarios[email] || usuarios[email].password !== pass) return alert('Correo o contraseña incorrectos.');
        usuarioActual = email;
        localStorage.setItem('sesion_activa', email);
        cargarPanelUsuario();
      }
    }

    function cargarPanelUsuario() {
      document.getElementById('vista-auth').style.display = 'none';
      document.getElementById('vista-inicio').style.display = 'flex';
      document.getElementById('user-display-email').innerText = usuarioActual;
      document.getElementById('badge-email-header').innerText = usuarioActual;
    }

    window.addEventListener('DOMContentLoaded', () => {
      const sesionGuardada = localStorage.getItem('sesion_activa');
      if (sesionGuardada) {
        usuarioActual = sesionGuardada;
        cargarPanelUsuario();
      }

      const hoy = new Date();
      const mesStr = hoy.getFullYear() + '-' + String(hoy.getMonth() + 1).padStart(2, '0');
      document.getElementById('selected-month').value = mesStr;
    });

    function cerrarSesion() {
      localStorage.removeItem('sesion_activa');
      location.reload();
    }

    function obtenerClaveStorage() {
      const mes = document.getElementById('selected-month').value || 'general';
      return 'usuario_gastos_' + usuarioActual + '_' + nombreUsuarioClave + '_' + mes;
    }

    function parseMonto(str) {
      if (!str) return 0;
      let limpio = str.toString().replace(/\./g, '').replace(',', '.');
      let val = parseFloat(limpio);
      return isNaN(val) ? 0 : val;
    }

    function formatMonto(num) {
      return num.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    // CARGA Y GUARDADO
    function cargarDatosUsuario() {
      const mesAnno = document.getElementById('selected-month').value;
      const tbody = document.getElementById('table-body');
      tbody.innerHTML = '';

      try {
        const datosGuardados = localStorage.getItem(obtenerClaveStorage());
        if (datosGuardados) {
          datosUsuario = JSON.parse(datosGuardados);
        } else {
          datosUsuario = { ingresos: "0,00", filas: [] };
        }
      } catch (e) {
        datosUsuario = { ingresos: "0,00", filas: [] };
      }

      document.getElementById('ingresos-input').value = datosUsuario.ingresos || "0,00";

      const filasACargar = datosUsuario.filas || [];

      if (filasACargar.length === 0) {
        agregarFila(false);
      } else {
        filasACargar.forEach(item => {
          const row = document.createElement('tr');
          const isDisabled = !item.tieneCuotas;
          row.innerHTML = `
            <td><input type="date" class="cell-input input-fecha" value="${item.fecha || ''}" onchange="guardarDatosUsuario()"></td>
            <td><input type="text" class="cell-input input-cat" list="categorias-list" value="${item.cat || ''}" onchange="guardarDatosUsuario()"></td>
            <td><input type="text" class="cell-input input-detalle" value="${item.detalle || ''}" onchange="guardarDatosUsuario()"></td>
            <td>
              <div class="cuota-container">
                <select class="select-cuotas-type" onchange="toggleModoCuotas(this)">
                  <option value="sin" ${!item.tieneCuotas ? 'selected' : ''}>Un pago</option>
                  <option value="con" ${item.tieneCuotas ? 'selected' : ''}>En cuotas</option>
                </select>
                <input type="text" class="cell-input input-cuota-val" value="${item.cuota || 'Un pago'}" style="text-align: center;" ${isDisabled ? 'disabled' : ''} onchange="guardarDatosUsuario()">
              </div>
            </td>
            <td><input type="text" class="cell-input input-fin-val" value="${item.fin || 'Este mes'}" style="text-align: center;" ${isDisabled ? 'disabled' : ''} onchange="guardarDatosUsuario()"></td>
            <td><input type="text" class="cell-input input-monto" value="${item.monto || '0,00'}" style="text-align: right; font-weight: 600;" oninput="calcularTotales()" onchange="guardarDatosUsuario()"></td>
            <td style="text-align: center;">${crearSelectEstado(item.estado || 'Pendiente')}</td>
            <td style="text-align: center;"><button onclick="borrarFila(this)" style="border:none; background:none; cursor:pointer;">❌</button></td>
          `;
          tbody.appendChild(row);
        });
      }

      calcularTotales();
    }

    function guardarDatosUsuario() {
      if (!nombreUsuarioClave || !usuarioActual) return;

      const rows = document.querySelectorAll('#table-body tr');
      const filas = [];

      rows.forEach(row => {
        const fecha = row.querySelector('.input-fecha')?.value || "";
        const cat = row.querySelector('.input-cat')?.value || "";
        const detalle = row.querySelector('.input-detalle')?.value || "";
        const tieneCuotas = row.querySelector('.select-cuotas-type')?.value === 'con';
        const cuota = row.querySelector('.input-cuota-val')?.value || "";
        const fin = row.querySelector('.input-fin-val')?.value || "";
        const monto = row.querySelector('.input-monto')?.value || "0,00";
        const estado = row.querySelector('.select-status')?.value || "Pendiente";

        if (detalle.trim() !== "" || parseMonto(monto) > 0) {
          filas.push({ fecha, cat, detalle, tieneCuotas, cuota, fin, monto, estado });
        }
      });

      datosUsuario = {
        ingresos: document.getElementById('ingresos-input').value,
        filas: filas
      };

      localStorage.setItem(obtenerClaveStorage(), JSON.stringify(datosUsuario));
    }

    function irAArchivosPersona() {
      const inputNom = document.getElementById('nombre-usuario').value.trim();
      if (!inputNom) return alert('Ingresa el nombre de la persona para continuar.');

      nombreUsuarioClave = inputNom.toLowerCase();
      document.getElementById('user-display').innerText = inputNom;
      
      document.getElementById('vista-inicio').style.display = 'none';
      document.getElementById('vista-panel').style.display = 'flex';
      
      cargarDatosUsuario();
    }

    function volverAInicio() {
      document.getElementById('vista-panel').style.display = 'none';
      document.getElementById('vista-inicio').style.display = 'flex';
    }

    function toggleModoCuotas(selectElem) {
      const parentRow = selectElem.closest('tr');
      const inputCuota = parentRow.querySelector('.input-cuota-val');
      const inputFin = parentRow.querySelector('.input-fin-val');

      if (selectElem.value === 'sin') {
        inputCuota.value = "Un pago";
        inputCuota.disabled = true;
        inputFin.value = "Este mes";
        inputFin.disabled = true;
      } else {
        inputCuota.value = "1 / 1";
        inputCuota.disabled = false;
        inputFin.disabled = false;
      }
      guardarDatosUsuario();
    }

    function crearSelectEstado(estadoActual) {
      const claseColor = getClaseEstado(estadoActual);
      return `
        <select class="select-status ${claseColor}" onchange="cambiarColorEstado(this)">
          <option value="Pendiente" ${estadoActual === 'Pendiente' ? 'selected' : ''}>⏳ Pendiente</option>
          <option value="Pagado" ${estadoActual === 'Pagado' ? 'selected' : ''}>✅ Pagado / Al día</option>
          <option value="Vencido" ${estadoActual === 'Vencido' ? 'selected' : ''}>🚨 Vencido</option>
          <option value="En Cuotas" ${estadoActual === 'En Cuotas' ? 'selected' : ''}>💳 En Cuotas</option>
        </select>
      `;
    }

    function getClaseEstado(valor) {
      if (valor === 'Pagado') return 'status-pagado';
      if (valor === 'Vencido') return 'status-vencido';
      if (valor === 'En Cuotas') return 'status-cuotas';
      return 'status-pendiente';
    }

    function cambiarColorEstado(selectElement) {
      selectElement.className = 'select-status ' + getClaseEstado(selectElement.value);
      guardarDatosUsuario();
    }

    function calcularTotales() {
      const filas = document.querySelectorAll('#table-body tr');
      let totalGastos = 0;

      filas.forEach(row => {
        const inputMonto = row.querySelector('.input-monto');
        if (inputMonto) {
          totalGastos += parseMonto(inputMonto.value);
        }
      });

      const ingresosStr = document.getElementById('ingresos-input').value;
      const totalIngresos = parseMonto(ingresosStr);
      const ahorro = totalIngresos - totalGastos;

      document.getElementById('total-gastos-val').innerText = `$${formatMonto(totalGastos)}`;

      const ahorroElem = document.getElementById('total-ahorro-val');
      const ahorroCard = document.getElementById('ahorro-card');
      ahorroElem.innerText = `$${formatMonto(ahorro)}`;

      if (ahorro < 0) {
        ahorroCard.className = 'summary-card negative';
        ahorroElem.style.color = 'var(--accent-red)';
      } else {
        ahorroCard.className = 'summary-card highlight';
        ahorroElem.style.color = 'var(--accent-green)';
      }
    }

    function marcarIngresoModificado() {
      calcularTotales();
      guardarDatosUsuario();
    }

    function agregarFila(autoSave = true) {
      const tbody = document.getElementById('table-body');
      const newRow = document.createElement('tr');
      const mesActual = document.getElementById('selected-month').value || "2026-08";

      newRow.innerHTML = `
        <td><input type="date" class="cell-input input-fecha" value="${mesActual}-01" onchange="guardarDatosUsuario()"></td>
        <td><input type="text" class="cell-input input-cat" list="categorias-list" placeholder="Categoría..." onchange="guardarDatosUsuario()"></td>
        <td><input type="text" class="cell-input input-detalle" placeholder="Nuevo gasto..." onchange="guardarDatosUsuario()"></td>
        <td>
          <div class="cuota-container">
            <select class="select-cuotas-type" onchange="toggleModoCuotas(this)">
              <option value="sin" selected>Un pago</option>
              <option value="con">En cuotas</option>
            </select>
            <input type="text" class="cell-input input-cuota-val" value="Un pago" style="text-align: center;" disabled onchange="guardarDatosUsuario()">
          </div>
        </td>
        <td><input type="text" class="cell-input input-fin-val" value="Este mes" style="text-align: center;" disabled onchange="guardarDatosUsuario()"></td>
        <td><input type="text" class="cell-input input-monto" value="0,00" style="text-align: right; font-weight: 600;" oninput="calcularTotales()" onchange="guardarDatosUsuario()"></td>
        <td style="text-align: center;">${crearSelectEstado('Pendiente')}</td>
        <td style="text-align: center;"><button onclick="borrarFila(this)" style="border:none; background:none; cursor:pointer;">❌</button></td>
      `;
      tbody.appendChild(newRow);
      calcularTotales();

      if (autoSave) {
        guardarDatosUsuario();
      }
    }

    function borrarFila(btn) {
      btn.closest('tr').remove();
      calcularTotales();
      guardarDatosUsuario();
    }

    function renovarMes() {
      guardarDatosUsuario();
      const picker = document.getElementById('selected-month');
      const mesActual = picker.value;

      const [yearStr, monthStr] = mesActual.split('-');
      let year = parseInt(yearStr, 10);
      let month = parseInt(monthStr, 10);

      month++;
      if (month > 12) {
        month = 1;
        year++;
      }

      const mesSiguiente = `${year}-${String(month).padStart(2, '0')}`;
      const nuevasFilas = [];

      (datosUsuario.filas || []).forEach(item => {
        let incluir = true;
        let nuevaCuotaStr = item.cuota;
        let nuevoEstado = "Pendiente";

        if (item.tieneCuotas && item.cuota && item.cuota.includes('/')) {
          const partes = item.cuota.split('/');
          let actual = parseInt(partes[0].trim(), 10);
          const total = parseInt(partes[1].trim(), 10);

          if (!isNaN(actual) && !isNaN(total)) {
            actual++;
            if (actual > total) {
              incluir = false;
            } else {
              nuevaCuotaStr = `${actual} / ${total}`;
              nuevoEstado = "En Cuotas";
            }
          }
        }

        if (incluir) {
          let dia = "01";
          if (item.fecha && item.fecha.includes('-')) {
            dia = item.fecha.split('-')[2];
          }

          nuevasFilas.push({
            ...item,
            fecha: `${mesSiguiente}-${dia}`,
            cuota: nuevaCuotaStr,
            estado: nuevoEstado
          });
        }
      });

      const claveSiguiente = 'usuario_gastos_' + usuarioActual + '_' + nombreUsuarioClave + '_' + mesSiguiente;
      const datosSiguientes = {
        ingresos: datosUsuario.ingresos,
        filas: nuevasFilas
      };

      localStorage.setItem(claveSiguiente, JSON.stringify(datosSiguientes));

      picker.value = mesSiguiente;
      cargarDatosUsuario();

      alert(`¡Clonado con éxito a ${mesSiguiente}! Se mantuvieron tus ingresos y las cuotas avanzaron.`);
    }

    // DRAG AND DROP COLUMNAS
    const table = document.getElementById('finance-table');
    let dragSrcIndex = null;

    table.querySelectorAll('th').forEach((th, index) => {
      if (!th.getAttribute('draggable')) return;

      th.addEventListener('dragstart', (e) => {
        dragSrcIndex = index;
        e.dataTransfer.effectAllowed = 'move';
      });

      th.addEventListener('dragover', (e) => e.preventDefault());

      th.addEventListener('drop', (e) => {
        e.preventDefault();
        const targetIndex = index;
        if (dragSrcIndex === null || dragSrcIndex === targetIndex) return;

        const rows = table.rows;
        for (let row of rows) {
          const cells = row.children;
          if (dragSrcIndex < targetIndex) {
            row.insertBefore(cells[dragSrcIndex], cells[targetIndex].nextSibling);
          } else {
            row.insertBefore(cells[dragSrcIndex], cells[targetIndex]);
          }
        }
      });
    });

    // ARCHIVOS EXCEL EXTERNOS
    function subirExcelWeb(input) {
      if (!input.files || !input.files[0]) return;

      const file = input.files[0];
      const formData = new FormData();
      formData.append('file', file);

      fetch('/importar-excel', { method: 'POST', body: formData })
      .then(res => res.json())
      .then(data => {
        if (data.error) alert('Error: ' + data.error);
        else mostrarTablaExcelStandalone(data.html, data.filename);
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
        if file.filename.endswith('.csv'): # type: ignore
            df = pd.read_csv(file) # type: ignore
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