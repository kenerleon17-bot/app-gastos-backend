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
  <title>Control de Gastos Personales</title>

  <style>
    :root {
      --bg-main: #F8FAFC;
      --bg-card: #FFFFFF;
      --primary-navy: #1E40AF;
      --primary-hover: #1D4ED8;
      --accent-green: #107C41;
      --accent-red: #A80000;
      --excel-green: #217346;
      --excel-border: #CBD5E1;
      --excel-bg-head: #F1F5F9;
      --text-main: #0F172A;
      --text-muted: #64748B;
      --border-color: #E2E8F0;
      --font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: var(--bg-main);
      color: var(--text-main);
      font-family: var(--font-family);
      min-height: 100vh;
      padding: 1rem;
      line-height: 1.5;
    }

    /* AUTENTICACIÓN Y ENTRADA */
    .welcome-wrapper {
      min-height: calc(100vh - 2rem);
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .welcome-container {
      width: 100%;
      max-width: 800px;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 20px;
      padding: 3.5rem 3rem;
      box-shadow: 0 20px 25px -5px rgba(0,0,0,0.05);
      text-align: center;
    }

    .welcome-title { font-size: 2.5rem; color: var(--primary-navy); font-weight: 800; margin-bottom: 0.5rem; }
    .welcome-subtitle { color: var(--text-muted); font-size: 1.1rem; margin-bottom: 2.5rem; }

    .form-user { display: flex; flex-direction: column; gap: 1.5rem; text-align: left; }
    .form-user label { font-weight: 700; font-size: 1.1rem; color: var(--text-main); }
    .form-user input { width: 100%; padding: 1rem 1.2rem; border: 2px solid var(--border-color); border-radius: 12px; font-size: 1.1rem; outline: none; }
    .form-user input:focus { border-color: var(--primary-navy); }

    .btn-stack { display: flex; flex-direction: column; gap: 1rem; margin-top: 1rem; }

    .btn {
      padding: 0.8rem 1.4rem;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.95rem;
      cursor: pointer;
      border: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: all 0.2s ease;
      text-decoration: none;
    }

    .btn-navy { background-color: var(--primary-navy); color: #ffffff; }
    .btn-navy:hover { background-color: var(--primary-hover); }

    .btn-excel-green { background-color: var(--excel-green); color: #ffffff; }
    .btn-excel-green:hover { background-color: #1a5c37; }

    .btn-outline { background-color: #FFFFFF; border: 1px solid var(--excel-border); color: var(--text-main); }
    .btn-outline:hover { background-color: #F8FAFC; border-color: #94A3B8; }

    /* PANEL PRINCIPAL (CONTROL MENSUAL) */
    .main-app { display: none; width: 100%; flex-direction: column; gap: 1rem; max-width: 1500px; margin: 0 auto; }

    .top-bar-excel {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-bottom: 3px solid var(--excel-green);
      border-radius: 12px;
      padding: 0.75rem 1.25rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      flex-wrap: wrap;
      box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    .brand-section { display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap; }
    .brand-title { font-weight: 800; font-size: 1.25rem; color: var(--excel-green); display: flex; align-items: center; gap: 0.4rem; }
    .user-pill { font-size: 0.85rem; background: #EFF6FF; color: var(--primary-navy); padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 700; border: 1px solid #BFDBFE; }

    .month-picker-container {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: #F1F5F9;
      border: 1px solid var(--excel-border);
      padding: 0.3rem 0.75rem;
      border-radius: 8px;
    }

    .top-actions { display: flex; gap: 0.6rem; align-items: center; }

    /* TABLA CONTROL MENSUAL */
    .excel-container {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1rem;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);
    }

    .table-wrapper { overflow-x: auto; min-height: 380px; max-height: 60vh; }

    .excel-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
      background: #FFFFFF;
    }

    .excel-table th {
      background-color: var(--excel-bg-head);
      color: var(--text-main);
      font-weight: 700;
      padding: 0.6rem 0.8rem;
      border: 1px solid var(--excel-border);
      text-align: left;
      position: sticky;
      top: 0;
      z-index: 10;
    }

    .excel-table td {
      padding: 0.4rem 0.6rem;
      border: 1px solid var(--excel-border);
      color: var(--text-main);
      background-color: #FFFFFF;
    }

    .cell-input {
      width: 100%;
      border: none;
      outline: none;
      background: transparent;
      font-family: inherit;
      font-size: inherit;
      color: inherit;
    }

    .excel-table tr.dragging { opacity: 0.4; background-color: #E2E8F0; }
    .excel-table tr:hover td { background-color: #F8FAFC; }

    .drag-handle { cursor: grab; text-align: center; color: var(--text-muted); font-weight: bold; user-select: none; width: 35px; }
    .drag-handle:active { cursor: grabbing; }

    .btn-delete-row { background: none; border: none; color: var(--accent-red); cursor: pointer; font-size: 1rem; }
    .btn-delete-row:hover { opacity: 0.7; }

    /* FOOTER DE TOTALES EN TARJETAS */
    .summary-footer {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-top: 3px solid var(--excel-green);
      padding: 1rem 1.5rem;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1.25rem;
      border-radius: 12px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    .summary-card {
      background: #F8FAFC;
      border: 1px solid var(--border-color);
      padding: 0.75rem 1rem;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      gap: 0.3rem;
    }

    .summary-card.highlight {
      background: #F0FDF4;
      border-color: #B7EB8F;
    }

    .summary-title { font-size: 0.75rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }

    .summary-input {
      font-size: 1.3rem;
      font-weight: 800;
      color: var(--accent-green);
      border: 1px dashed #94A3B8;
      background: #FFFFFF;
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
      outline: none;
      width: 100%;
    }

    .summary-value { font-size: 1.4rem; font-weight: 800; }

    .excel-standalone-view {
      display: none; width: 100%; background-color: var(--bg-card);
      border: 1px solid var(--border-color); border-radius: 16px; padding: 2rem;
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
          <button class="btn btn-navy" onclick="irAArchivosPersona()">📁 2. Ir a la Planilla de Gastos</button>
          <input type="file" id="input-excel" accept=".xlsx, .xls, .csv" style="display: none;" onchange="subirExcelWeb(this)">
          <button class="btn btn-outline" onclick="document.getElementById('input-excel').click()">📊 Importar Excel Externo</button>
          <button class="btn btn-outline" style="color: var(--accent-red);" onclick="cerrarSesion()">🚪 Cerrar Sesión</button>
        </div>
      </div>
    </div>
  </div>

  <!-- PANEL PRINCIPAL: CONTROL MENSUAL -->
  <div class="main-app" id="vista-panel">
    
    <!-- BARRA SUPERIOR -->
    <header class="top-bar-excel">
      <div class="brand-section">
        <span class="brand-title">📊 Control Mensual</span>
        <span class="user-pill" id="badge-usuario">Persona</span>
        <span class="user-pill" id="badge-email-header">kenerleon17@gmail.com</span>
        
        <div class="month-picker-container">
          <span style="font-size: 0.85rem; font-weight: 700; color: var(--text-muted);">📅 Mes:</span>
          <input type="month" id="selected-month" class="cell-input" value="2026-08" style="font-weight: 700; cursor: pointer;" onchange="cargarDatosUsuario()">
        </div>
      </div>

      <div class="top-actions">
        <button class="btn btn-outline" onclick="clonarSiguienteMes()">🔄 Clonar a Siguiente Mes</button>
        <button class="btn btn-excel-green" onclick="agregarFilaVacia()">+ Nueva Fila</button>
        <button class="btn btn-outline" onclick="volverAInicio()">🗙 Menú</button>
      </div>
    </header>

    <!-- TABLA INTERACTIVA ESTILO CONTROL MENSUAL -->
    <section class="excel-container">
      <div class="table-wrapper">
        <table class="excel-table">
          <thead>
            <tr>
              <th style="width: 35px; text-align: center;">::</th>
              <th style="width: 140px;">:: Fecha Venc.</th>
              <th style="width: 160px;">:: Categoría</th>
              <th>:: Concepto / Detalle</th>
              <th style="width: 140px;">:: Modo / Cuotas</th>
              <th style="width: 140px;">:: Fin de Pago</th>
              <th style="width: 150px; text-align: right;">:: Monto ($)</th>
              <th style="width: 150px; text-align: center;">:: Estado (Fijar)</th>
              <th style="width: 40px; text-align: center;">⚙️</th>
            </tr>
          </thead>
          <tbody id="tbody-excel">
          </tbody>
        </table>
      </div>
    </section>

    <!-- FOOTER DE RESUMEN FINANCIERO -->
    <footer class="summary-footer">
      <div class="summary-card">
        <span class="summary-title">💵 INGRESOS DEL MES</span>
        <input type="text" id="ingresos-input" class="summary-input" value="0,00" oninput="guardarIngresoActual()">
      </div>

      <div class="summary-card">
        <span class="summary-title">📉 TOTAL GASTOS</span>
        <span id="total-gastos-val" class="summary-value" style="color: var(--accent-red);">$0,00</span>
      </div>

      <div class="summary-card highlight">
        <span class="summary-title">💰 DISPONIBLE PARA AHORRO</span>
        <span id="total-ahorro-val" class="summary-value" style="color: var(--accent-green);">$0,00</span>
      </div>
    </footer>

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
    let datosUsuario = { ingresos: 0, categorias: ['Servicios', 'Alquiler', 'Comida', 'Varios'], listaGastos: [] };

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

    function parsearMontoFlexible(montoStr) {
      if (typeof montoStr === 'number') return montoStr;
      if (!montoStr) return 0;
      let str = montoStr.toString().trim();
      if (str.includes('.') && str.includes(',')) str = str.replace(/\./g, '').replace(',', '.');
      else if (str.includes(',')) str = str.replace(',', '.');
      const num = parseFloat(str);
      return isNaN(num) ? 0 : num;
    }

    function formatearMoneda(monto) {
      return '$' + monto.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    // CARGA Y GUARDADO
    function cargarDatosUsuario() {
      try {
        const datosGuardados = localStorage.getItem(obtenerClaveStorage());
        if (datosGuardados) {
          datosUsuario = JSON.parse(datosGuardados);
          if (!datosUsuario.categorias) datosUsuario.categorias = ['Servicios', 'Alquiler', 'Comida', 'Varios'];
        } else {
          datosUsuario = { ingresos: 0, categorias: ['Servicios', 'Alquiler', 'Comida', 'Varios'], listaGastos: [] };
        }
      } catch (e) {
        datosUsuario = { ingresos: 0, categorias: ['Servicios', 'Alquiler', 'Comida', 'Varios'], listaGastos: [] };
      }
      document.getElementById('ingresos-input').value = formatearMoneda(datosUsuario.ingresos || 0).replace('$', '');
      actualizarPantallaPanel();
    }

    function guardarDatosUsuario() {
      if (nombreUsuarioClave && usuarioActual) {
        localStorage.setItem(obtenerClaveStorage(), JSON.stringify(datosUsuario));
      }
    }

    function irAArchivosPersona() {
      const inputNom = document.getElementById('nombre-usuario').value.trim();
      if (!inputNom) return alert('Ingresa el nombre de la persona para continuar.');
      
      nombreUsuarioClave = inputNom.toLowerCase();
      document.getElementById('badge-usuario').innerText = inputNom;
      cargarDatosUsuario();

      document.getElementById('vista-inicio').style.display = 'none';
      document.getElementById('vista-panel').style.display = 'flex';
    }

    function volverAInicio() {
      document.getElementById('vista-panel').style.display = 'none';
      document.getElementById('vista-inicio').style.display = 'flex';
    }

    function guardarIngresoActual() {
      const val = parsearMontoFlexible(document.getElementById('ingresos-input').value);
      datosUsuario.ingresos = val;
      guardarDatosUsuario();
      actualizarPantallaPanel();
    }

    function agregarFilaVacia() {
      const hoyStr = new Date().toISOString().split('T')[0];
      datosUsuario.listaGastos.push({
        id: Date.now(),
        fecha: hoyStr,
        categoria: datosUsuario.categorias[0] || 'Varios',
        concepto: '',
        modo: 'Un pago',
        finPago: 'Este mes',
        monto: 0,
        estado: 'pendiente'
      });
      guardarDatosUsuario();
      actualizarPantallaPanel();
    }

    function eliminarFila(id) {
      datosUsuario.listaGastos = datosUsuario.listaGastos.filter(item => item.id !== id);
      guardarDatosUsuario();
      actualizarPantallaPanel();
    }

    function actualizarPantallaPanel() {
      let totalGastos = 0;
      datosUsuario.listaGastos.forEach(g => totalGastos += (parseFloat(g.monto) || 0));

      const ingresos = datosUsuario.ingresos || 0;
      const ahorro = ingresos - totalGastos;

      document.getElementById('total-gastos-val').innerText = formatearMoneda(totalGastos);
      
      const ahorroElem = document.getElementById('total-ahorro-val');
      ahorroElem.innerText = formatearMoneda(ahorro);
      ahorroElem.style.color = ahorro < 0 ? 'var(--accent-red)' : 'var(--accent-green)';

      renderTablaExcel();
    }

    // RENDERIZADO DE TABLA ESTILO CONTROL MENSUAL
    function renderTablaExcel() {
      const tbody = document.getElementById('tbody-excel');
      tbody.innerHTML = '';

      if (datosUsuario.listaGastos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: var(--text-muted); padding: 2rem;">La planilla está vacía. Haz clic en "+ Nueva Fila" para agregar gastos.</td></tr>';
        return;
      }

      datosUsuario.listaGastos.forEach((item, index) => {
        const tr = document.createElement('tr');
        tr.draggable = true;
        tr.dataset.index = index;

        let catOptionsHTML = datosUsuario.categorias.map(c => 
          '<option value="' + c + '" ' + (c === item.categoria ? 'selected' : '') + '>' + c + '</option>'
        ).join('');

        tr.innerHTML = `
          <td class="drag-handle">≡</td>
          <td>
            <input type="date" class="cell-input" value="${item.fecha || ''}" onchange="actualizarCelda(${item.id}, 'fecha', this.value)">
          </td>
          <td>
            <select class="cell-input" style="font-weight:bold; color: var(--primary-navy);" onchange="actualizarCelda(${item.id}, 'categoria', this.value)">
              ${catOptionsHTML}
            </select>
          </td>
          <td>
            <input type="text" class="cell-input" placeholder="Detalle..." value="${item.concepto || ''}" onchange="actualizarCelda(${item.id}, 'concepto', this.value)">
          </td>
          <td>
            <input type="text" class="cell-input" style="text-align: center;" value="${item.modo || 'Un pago'}" onchange="actualizarCelda(${item.id}, 'modo', this.value)">
          </td>
          <td>
            <input type="text" class="cell-input" style="text-align: center;" value="${item.finPago || 'Este mes'}" onchange="actualizarCelda(${item.id}, 'finPago', this.value)">
          </td>
          <td>
            <input type="text" class="cell-input" style="text-align: right; font-weight: 700; color: var(--accent-red);" value="${formatearMoneda(item.monto || 0).replace('$', '')}" onchange="actualizarCeldaMonto(${item.id}, this.value)">
          </td>
          <td style="text-align: center;">
            <select class="cell-input" style="text-align-last: center; font-weight: 700;" onchange="actualizarCelda(${item.id}, 'estado', this.value)">
              <option value="pendiente" ${item.estado === 'pendiente' ? 'selected' : ''}>⏳ Pendiente</option>
              <option value="pagado" ${item.estado === 'pagado' ? 'selected' : ''}>✅ Pagado</option>
            </select>
          </td>
          <td style="text-align: center;">
            <button class="btn-delete-row" onclick="eliminarFila(${item.id})" title="Eliminar fila">🗑️</button>
          </td>
        `;

        // Eventos Drag and Drop
        tr.addEventListener('dragstart', handleDragStart);
        tr.addEventListener('dragover', handleDragOver);
        tr.addEventListener('drop', handleDrop);
        tr.addEventListener('dragend', handleDragEnd);

        tbody.appendChild(tr);
      });
    }

    function actualizarCelda(id, campo, valor) {
      const item = datosUsuario.listaGastos.find(g => g.id === id);
      if (item) {
        item[campo] = valor;
        guardarDatosUsuario();
      }
    }

    function actualizarCeldaMonto(id, valorTexto) {
      const item = datosUsuario.listaGastos.find(g => g.id === id);
      if (item) {
        item.monto = parsearMontoFlexible(valorTexto);
        guardarDatosUsuario();
        actualizarPantallaPanel();
      }
    }

    function clonarSiguienteMes() {
      const picker = document.getElementById('selected-month');
      if (!picker.value) return;

      const [year, month] = picker.value.split('-').map(Number);
      let nextYear = year;
      let nextMonth = month + 1;
      if (nextMonth > 12) {
        nextMonth = 1;
        nextYear++;
      }

      const nextMonthStr = nextYear + '-' + String(nextMonth).padStart(2, '0');
      const claveSiguiente = 'usuario_gastos_' + usuarioActual + '_' + nombreUsuarioClave + '_' + nextMonthStr;

      if (localStorage.getItem(claveSiguiente)) {
        if (!confirm(`El mes ${nextMonthStr} ya tiene datos registrados. ¿Quieres sobrescribirlo?`)) return;
      }

      localStorage.setItem(claveSiguiente, JSON.stringify(datosUsuario));
      picker.value = nextMonthStr;
      cargarDatosUsuario();
      alert(`¡Planilla clonada exitosamente al mes ${nextMonthStr}!`);
    }

    // ARRASTRAR Y MOVER FILAS (DRAG & DROP)
    let dragSrcIndex = null;

    function handleDragStart(e) {
      dragSrcIndex = this.dataset.index;
      this.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
    }

    function handleDragOver(e) {
      if (e.preventDefault) e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      return false;
    }

    function handleDrop(e) {
      if (e.stopPropagation) e.stopPropagation();
      const targetIndex = this.dataset.index;

      if (dragSrcIndex !== null && dragSrcIndex !== targetIndex) {
        const elementoMovido = datosUsuario.listaGastos.splice(dragSrcIndex, 1)[0];
        datosUsuario.listaGastos.splice(targetIndex, 0, elementoMovido);
        guardarDatosUsuario();
        actualizarPantallaPanel();
      }
      return false;
    }

    function handleDragEnd() {
      this.classList.remove('dragging');
    }

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