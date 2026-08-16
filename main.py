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
      --accent-green: #16A34A;
      --accent-red: #DC2626;
      --text-main: #0F172A;
      --text-muted: #64748B;
      --border-color: #E2E8F0;
      --table-border: #CBD5E1;
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

    /* PANTALLAS DE ENTRADA */
    .welcome-wrapper {
      min-height: calc(100vh - 3rem);
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
      padding: 0.9rem 1.5rem;
      border-radius: 12px;
      font-weight: 600;
      font-size: 1rem;
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

    .btn-outline { background-color: #FFFFFF; border: 2px solid var(--border-color); color: var(--text-main); }
    .btn-outline:hover { background-color: #F8FAFC; border-color: #94A3B8; }

    .btn-sm { padding: 0.5rem 0.9rem; font-size: 0.9rem; border-radius: 8px; }

    /* APLICACIÓN PRINCIPAL */
    .main-app { display: none; width: 100%; flex-direction: column; gap: 1.5rem; max-width: 1400px; margin: 0 auto; }

    .header-top {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 1rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    .header-user-info { display: flex; align-items: center; gap: 1rem; }
    .user-badge { background-color: #EFF6FF; color: var(--primary-navy); padding: 0.4rem 0.8rem; border-radius: 10px; font-weight: 800; font-size: 1.2rem; border: 1px solid #BFDBFE; }

    .summary-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.25rem; }
    .stat-card { background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 1.25rem; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .stat-card.balance { border-left: 5px solid var(--primary-navy); }
    .stat-card.ingresos { border-left: 5px solid var(--accent-green); }
    .stat-card.gastos { border-left: 5px solid var(--accent-red); }
    .stat-title { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 700; }
    .stat-value { font-size: 2rem; font-weight: 800; margin-top: 0.25rem; }

    /* CONTROLES SUPERIORES (BARRA DE AGREGAR CATEGO / GASTOS) */
    .top-controls-panel {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 1.5rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.02);
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    .controls-title {
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--primary-navy);
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 0.5rem;
    }

    .controls-grid {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 1.5rem;
    }

    .add-gasto-form {
      display: grid;
      grid-template-columns: 1.2fr 1.5fr 2fr 1.2fr auto;
      gap: 0.75rem;
      align-items: end;
    }

    .add-cat-form {
      display: flex;
      gap: 0.5rem;
      align-items: end;
      border-left: 2px solid var(--border-color);
      padding-left: 1.5rem;
    }

    .field-group { display: flex; flex-direction: column; gap: 0.3rem; }
    .field-group label { font-size: 0.85rem; font-weight: 700; color: var(--text-muted); }
    .field-group input, .field-group select {
      padding: 0.7rem 0.9rem;
      border: 1px solid var(--table-border);
      border-radius: 8px;
      font-size: 0.95rem;
      outline: none;
      background: #FFFFFF;
    }
    .field-group input:focus, .field-group select:focus { border-color: var(--primary-navy); }

    /* TABLA ESTILO EXCEL */
    .excel-container {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 1.5rem;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);
    }

    .table-wrapper { overflow-x: auto; max-height: 60vh; }

    .excel-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
      background: #FFFFFF;
    }

    .excel-table th {
      background-color: #F1F5F9;
      color: var(--primary-navy);
      font-weight: 700;
      padding: 0.8rem 1rem;
      border: 1px solid var(--table-border);
      text-align: left;
      position: sticky;
      top: 0;
      z-index: 10;
    }

    .excel-table td {
      padding: 0.7rem 1rem;
      border: 1px solid var(--table-border);
      color: var(--text-main);
      background-color: #FFFFFF;
    }

    .excel-table tr.dragging {
      opacity: 0.4;
      background-color: #E2E8F0;
    }

    .excel-table tr:hover td {
      background-color: #F8FAFC;
    }

    .drag-handle {
      cursor: grab;
      text-align: center;
      color: var(--text-muted);
      font-weight: bold;
      user-select: none;
      width: 40px;
    }
    .drag-handle:active { cursor: grabbing; }

    .editable-cell { outline: none; }
    .editable-cell:focus {
      background-color: #EFF6FF !important;
      box-shadow: inset 0 0 0 2px var(--primary-navy);
    }

    .badge-cat {
      display: inline-block;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      font-size: 0.85rem;
      font-weight: 600;
      background-color: #E0E7FF;
      color: #3730A3;
    }

    .btn-delete-row {
      background: none;
      border: none;
      color: var(--accent-red);
      cursor: pointer;
      font-size: 1.1rem;
    }
    .btn-delete-row:hover { opacity: 0.7; }

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

  <!-- SELECCIÓN -->
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
          <button class="btn btn-navy" onclick="irAArchivosPersona()">📂 2. Ir a la Planilla de Gastos</button>
          <input type="file" id="input-excel" accept=".xlsx, .xls, .csv" style="display: none;" onchange="subirExcelWeb(this)">
          <button class="btn btn-outline" onclick="document.getElementById('input-excel').click()">📊 Importar Excel Externo</button>
          <button class="btn btn-outline" style="color: var(--accent-red);" onclick="cerrarSesion()">🚪 Cerrar Sesión</button>
        </div>
      </div>
    </div>
  </div>

  <!-- PANEL PRINCIPAL (PLANILLA TIPO EXCEL CON CONTROLES) -->
  <div class="main-app" id="vista-panel">
    <header class="header-top">
      <div class="header-user-info">
        <span class="user-badge" id="badge-usuario">Persona</span>
        <div>
          <h1 style="font-size: 1.5rem; color: var(--primary-navy); font-weight: 800;">Planilla Interactiva de Gastos</h1>
          <p style="color: var(--text-muted); font-size: 0.9rem;">Edita directamente sobre las celdas o arrastra las filas para reordenarlas</p>
        </div>
      </div>
      <button class="btn btn-outline" onclick="volverAInicio()">🏠 Volver al Inicio</button>
    </header>

    <!-- RESUMEN DE BALANCE -->
    <section class="summary-grid">
      <div class="stat-card balance">
        <span class="stat-title">Balance Disponible</span>
        <div class="stat-value" id="val-balance">$0,00</div>
      </div>
      <div class="stat-card ingresos">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span class="stat-title">Ingresos Mensuales</span>
          <button class="btn btn-outline btn-sm" onclick="modificarIngreso()">✏️ Editar</button>
        </div>
        <div class="stat-value" id="val-ingresos" style="color: var(--accent-green);">$0,00</div>
      </div>
      <div class="stat-card gastos">
        <span class="stat-title">Total Gastos</span>
        <div class="stat-value" id="val-gastos" style="color: var(--accent-red);">$0,00</div>
      </div>
    </section>

    <!-- PANEL SUPERIOR DE CONTROLES Y AGREGADO RÁPIDO -->
    <section class="top-controls-panel">
      <div class="controls-title">⚡ Opciones de Registro Rápido</div>
      <div class="controls-grid">
        
        <!-- AGREGAR GASTO -->
        <form class="add-gasto-form" onsubmit="agregarGastoFila(event)">
          <div class="field-group">
            <label>Fecha</label>
            <input type="date" id="input-fecha" required>
          </div>
          <div class="field-group">
            <label>Categoría</label>
            <select id="select-categoria" required>
              <option value="Servicios">Servicios</option>
              <option value="Alquiler">Alquiler</option>
              <option value="Comida">Comida</option>
              <option value="Varios">Varios</option>
            </select>
          </div>
          <div class="field-group">
            <label>Concepto / Descripción</label>
            <input type="text" id="input-concepto" placeholder="Ej: Pago de Luz" required autocomplete="off">
          </div>
          <div class="field-group">
            <label>Monto ($)</label>
            <input type="text" id="input-monto" placeholder="Ej: 15000" required autocomplete="off">
          </div>
          <button type="submit" class="btn btn-navy">+ Añadir a Tabla</button>
        </form>

        <!-- AGREGAR CATEGORÍA -->
        <form class="add-cat-form" onsubmit="crearNuevaCategoria(event)">
          <div class="field-group" style="flex-grow: 1;">
            <label>Nueva Categoría</label>
            <input type="text" id="input-nueva-cat" placeholder="Ej: Gimnasio" required autocomplete="off">
          </div>
          <button type="submit" class="btn btn-outline">+ Crear</button>
        </form>

      </div>
    </section>

    <!-- TABLA TIPO EXCEL -->
    <section class="excel-container">
      <div class="table-wrapper">
        <table class="excel-table">
          <thead>
            <tr>
              <th style="width: 40px; text-align: center;">Mover</th>
              <th style="width: 130px;">Fecha</th>
              <th style="width: 180px;">Categoría</th>
              <th>Concepto / Descripción</th>
              <th style="width: 160px; text-align: right;">Monto ($)</th>
              <th style="width: 50px; text-align: center;">Acción</th>
            </tr>
          </thead>
          <tbody id="tbody-excel">
            <!-- Filas dinámicas -->
          </tbody>
        </table>
      </div>
    </section>
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
    }

    window.addEventListener('DOMContentLoaded', () => {
      const sesionGuardada = localStorage.getItem('sesion_activa');
      if (sesionGuardada) {
        usuarioActual = sesionGuardada;
        cargarPanelUsuario();
      }
      document.getElementById('input-fecha').valueAsDate = new Date();
    });

    function cerrarSesion() {
      localStorage.removeItem('sesion_activa');
      location.reload();
    }

    function obtenerClaveStorage() {
      return `usuario_gastos_${usuarioActual}_${nombreUsuarioClave}`;
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

    // CARGAR Y GUARDAR
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
      actualizarSelectCategorias();
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

    function actualizarSelectCategorias() {
      const select = document.getElementById('select-categoria');
      select.innerHTML = '';
      datosUsuario.categorias.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.innerText = cat;
        select.appendChild(option);
      });
    }

    function crearNuevaCategoria(e) {
      e.preventDefault();
      const input = document.getElementById('input-nueva-cat');
      const nuevaCat = input.value.trim();
      if (nuevaCat && !datosUsuario.categorias.includes(nuevaCat)) {
        datosUsuario.categorias.push(nuevaCat);
        guardarDatosUsuario();
        actualizarSelectCategorias();
        document.getElementById('select-categoria').value = nuevaCat;
        input.value = '';
        renderTablaExcel();
      }
    }

    function agregarGastoFila(e) {
      e.preventDefault();
      const fecha = document.getElementById('input-fecha').value;
      const categoria = document.getElementById('select-categoria').value;
      const concepto = document.getElementById('input-concepto').value.trim();
      const monto = parsearMontoFlexible(document.getElementById('input-monto').value);

      datosUsuario.listaGastos.unshift({ id: Date.now(), fecha, categoria, concepto, monto });
      guardarDatosUsuario();
      actualizarPantallaPanel();

      document.getElementById('input-concepto').value = '';
      document.getElementById('input-monto').value = '';
    }

    function modificarIngreso() {
      const nuevoIngreso = prompt('Ingresa el monto del Ingreso Mensual:', datosUsuario.ingresos);
      if (nuevoIngreso !== null) {
        datosUsuario.ingresos = parsearMontoFlexible(nuevoIngreso);
        guardarDatosUsuario();
        actualizarPantallaPanel();
      }
    }

    function eliminarFila(id) {
      datosUsuario.listaGastos = datosUsuario.listaGastos.filter(item => item.id !== id);
      guardarDatosUsuario();
      actualizarPantallaPanel();
    }

    function actualizarPantallaPanel() {
      let totalGastos = 0;
      datosUsuario.listaGastos.forEach(g => totalGastos += (parseFloat(g.monto) || 0));

      document.getElementById('val-ingresos').innerText = formatearMoneda(datosUsuario.ingresos);
      document.getElementById('val-gastos').innerText = formatearMoneda(totalGastos);

      const balance = datosUsuario.ingresos - totalGastos;
      const valBalanceElem = document.getElementById('val-balance');
      valBalanceElem.innerText = formatearMoneda(balance);
      valBalanceElem.style.color = balance < 0 ? 'var(--accent-red)' : 'var(--text-main)';

      renderTablaExcel();
    }

    // RENDER DE TABLA EXCEL + EDICIÓN DIRECTA
    function renderTablaExcel() {
      const tbody = document.getElementById('tbody-excel');
      tbody.innerHTML = '';

      if (datosUsuario.listaGastos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">La planilla está vacía. Agrega items desde el panel superior.</td></tr>`;
        return;
      }

      datosUsuario.listaGastos.forEach((item, index) => {
        const tr = document.createElement('tr');
        tr.draggable = true;
        tr.dataset.index = index;

        // Opciones de Select de Categoría dentro de la celda
        let catOptionsHTML = datosUsuario.categorias.map(c => 
          `<option value="${c}" ${c === item.categoria ? 'selected' : ''}>${c}</option>`
        ).join('');

        tr.innerHTML = `
          <td class="drag-handle">≡</td>
          <td>
            <input type="date" value="${item.fecha}" style="border:none; background:transparent; font-family:inherit;" onchange="actualizarCelda(${item.id}, 'fecha', this.value)">
          </td>
          <td>
            <select style="border:none; background:transparent; font-weight:bold; color: var(--primary-navy);" onchange="actualizarCelda(${item.id}, 'categoria', this.value)">
              ${catOptionsHTML}
            </select>
          </td>
          <td class="editable-cell" contenteditable="true" onblur="actualizarCelda(${item.id}, 'concepto', this.innerText)">${item.concepto}</td>
          <td class="editable-cell" contenteditable="true" style="text-align: right; font-weight: 700; color: var(--accent-red);" onblur="actualizarCeldaMonto(${item.id}, this.innerText)">
            ${formatearMoneda(item.monto)}
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

    // LÓGICA DE DRAG & DROP (ARRASTRAR Y MOVER FILAS)
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

    // EXCEL EXTERNO
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