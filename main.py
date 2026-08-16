import os
import pandas as pd
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Control de Gastos Personales - Estilo Excel Pro</title>
  <style>
    :root {
      --excel-green: #107C41;
      --excel-green-hover: #0F6C38;
      --excel-header-bg: #F3F3F3;
      --excel-border: #D4D4D4;
      --excel-cell-border: #E0E0E0;
      --excel-selected: #107C41;
      --bg-main: #F8F9FA;
      --text-main: #212529;
      --text-muted: #6C757D;
      --accent-red: #D9534F;
      --accent-blue: #0275D8;
      --font-family: 'Segoe UI', system-ui, -apple-system, Roboto, sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: var(--bg-main);
      color: var(--text-main);
      font-family: var(--font-family);
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    /* VISTA AUTENTICACIÓN */
    .welcome-wrapper {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
      background: #EFEFEF;
    }

    .welcome-container {
      width: 100%;
      max-width: 480px;
      background: #FFFFFF;
      border: 1px solid var(--excel-border);
      border-radius: 8px;
      padding: 2.5rem;
      box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    }

    .welcome-title { font-size: 1.8rem; color: var(--excel-green); font-weight: 700; margin-bottom: 0.5rem; text-align: center; }
    .welcome-subtitle { color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1.5rem; text-align: center; }

    .form-user { display: flex; flex-direction: column; gap: 1rem; }
    .form-user label { font-weight: 600; font-size: 0.85rem; color: var(--text-main); }
    .form-user input { width: 100%; padding: 0.6rem 0.8rem; border: 1px solid var(--excel-border); border-radius: 4px; font-size: 0.95rem; outline: none; }
    .form-user input:focus { border-color: var(--excel-green); }

    .btn {
      padding: 0.6rem 1.2rem;
      border-radius: 4px;
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      border: 1px solid transparent;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: all 0.15s ease;
    }

    .btn-green { background-color: var(--excel-green); color: #ffffff; }
    .btn-green:hover { background-color: var(--excel-green-hover); }

    .btn-outline { background-color: #FFFFFF; border-color: var(--excel-border); color: var(--text-main); }
    .btn-outline:hover { background-color: #F3F3F3; }

    /* LAYOUT FULLSCREEN ESTILO EXCEL */
    .excel-app {
      display: none;
      flex-direction: column;
      height: 100vh;
      width: 100vw;
    }

    /* BARRA SUPERIOR EXCEL (RIBBON & TOOLBAR) */
    .excel-ribbon {
      background-color: var(--excel-green);
      color: white;
      padding: 0.5rem 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .excel-title-area { display: flex; align-items: center; gap: 0.8rem; }
    .excel-logo { font-weight: 900; font-size: 1.2rem; background: white; color: var(--excel-green); padding: 0.1rem 0.5rem; border-radius: 3px; }
    .excel-doc-title { font-weight: 600; font-size: 1.05rem; }

    .excel-toolbar {
      background-color: var(--excel-header-bg);
      border-bottom: 1px solid var(--excel-border);
      padding: 0.4rem 1rem;
      display: flex;
      gap: 1.5rem;
      align-items: center;
      flex-wrap: wrap;
    }

    .toolbar-group { display: flex; align-items: center; gap: 0.5rem; }
    .toolbar-label { font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }

    /* DASHBOARD CARDS / RESUMEN */
    .excel-summary-bar {
      background-color: #FFFFFF;
      border-bottom: 1px solid var(--excel-border);
      padding: 0.6rem 1.5rem;
      display: flex;
      gap: 2rem;
      align-items: center;
    }

    .stat-box { display: flex; flex-direction: column; }
    .stat-box .lbl { font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: var(--text-muted); }
    .stat-box .val { font-size: 1.25rem; font-weight: 800; }

    /* BARRA DE FÓRMULAS */
    .formula-bar {
      display: flex;
      align-items: center;
      background: white;
      border-bottom: 1px solid var(--excel-border);
      padding: 0.25rem 0.5rem;
      gap: 0.5rem;
    }

    .cell-name-box {
      width: 60px;
      text-align: center;
      font-weight: 600;
      font-size: 0.85rem;
      border: 1px solid var(--excel-border);
      background: #F8F9FA;
      padding: 0.1rem 0.3rem;
    }

    .fx-btn { font-weight: bold; font-style: italic; color: var(--text-muted); padding: 0 0.4rem; font-size: 0.9rem; }

    .formula-input-container { flex: 1; }
    .formula-input-container input {
      width: 100%;
      border: 1px solid var(--excel-border);
      padding: 0.2rem 0.5rem;
      font-family: monospace;
      font-size: 0.9rem;
      outline: none;
    }

    /* GRILLA DE EXCEL GIGANTE */
    .grid-container {
      flex: 1;
      overflow: auto;
      position: relative;
      background: #FFFFFF;
    }

    .excel-grid {
      border-collapse: collapse;
      table-layout: fixed;
      width: 100%;
      min-width: 1200px;
      font-size: 0.88rem;
    }

    .excel-grid th {
      background-color: var(--excel-header-bg);
      border: 1px solid var(--excel-border);
      color: #444;
      font-weight: 600;
      text-align: center;
      padding: 0.35rem;
      user-select: none;
      position: sticky;
      top: 0;
      z-index: 10;
    }

    .excel-grid th.col-row-num {
      width: 50px;
      background-color: var(--excel-header-bg);
      z-index: 11;
      left: 0;
    }

    .excel-grid td.row-num {
      background-color: var(--excel-header-bg);
      border: 1px solid var(--excel-border);
      text-align: center;
      color: #666;
      font-weight: 600;
      position: sticky;
      left: 0;
      z-index: 5;
      user-select: none;
    }

    .excel-grid td {
      border: 1px solid var(--excel-cell-border);
      padding: 0.3rem 0.5rem;
      outline: none;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      background: #FFFFFF;
    }

    .excel-grid td:focus {
      border: 2px solid var(--excel-selected) !important;
      background-color: #E8F5E9 !important;
      z-index: 2;
    }

    .excel-grid tr.dragging { opacity: 0.4; background: #E0E0E0; }

    .drag-handle {
      cursor: grab;
      text-align: center;
      color: #999;
      font-weight: bold;
    }

    /* BARRA DE ESTADO / PESTAÑAS ABAJO */
    .excel-bottom-bar {
      background-color: var(--excel-header-bg);
      border-top: 1px solid var(--excel-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.2rem 1rem;
      font-size: 0.8rem;
    }

    .excel-tabs { display: flex; gap: 0.2rem; }
    .excel-tab {
      background: #E0E0E0;
      padding: 0.3rem 1rem;
      border: 1px solid var(--excel-border);
      border-bottom: none;
      border-radius: 4px 4px 0 0;
      font-weight: 600;
      color: #555;
      cursor: pointer;
    }
    .excel-tab.active { background: #FFFFFF; color: var(--excel-green); border-top: 2px solid var(--excel-green); }

    .input-sm {
      padding: 0.3rem 0.5rem;
      border: 1px solid var(--excel-border);
      border-radius: 3px;
      font-size: 0.85rem;
    }
  </style>
</head>
<body>

  <!-- AUTENTICACIÓN -->
  <div class="welcome-wrapper" id="vista-auth">
    <div class="welcome-container">
      <h1 class="welcome-title" id="auth-titulo">Iniciar Sesión</h1>
      <p class="welcome-subtitle" id="auth-subtitulo">Planilla de Control de Gastos Excel Pro</p>

      <form class="form-user" onsubmit="procesarAuth(event)">
        <div>
          <label for="auth-email">Correo Electrónico</label>
          <input type="email" id="auth-email" placeholder="usuario@ejemplo.com" required autocomplete="off">
        </div>
        <div>
          <label for="auth-pass">Contraseña</label>
          <input type="password" id="auth-pass" placeholder="••••••••" required autocomplete="off">
        </div>

        <button type="submit" class="btn btn-green" id="auth-btn-submit" style="margin-top: 0.5rem;">Entrar al Sistema</button>
        <button type="button" class="btn btn-outline" onclick="alternarModoAuth()">
          <span id="auth-toggle-msg">¿No tienes cuenta? Regístrate aquí</span>
        </button>
      </form>
    </div>
  </div>

  <!-- SELECCIÓN DE PERSONA -->
  <div class="welcome-wrapper" id="vista-inicio" style="display: none;">
    <div class="welcome-container">
      <h1 class="welcome-title">Control de Gastos</h1>
      <p class="welcome-subtitle">Bienvenido, <span id="user-display-email" style="font-weight: bold; color: var(--excel-green);"></span></p>

      <div class="form-user">
        <div>
          <label for="nombre-usuario">Nombre de la Planilla / Persona:</label>
          <input type="text" id="nombre-usuario" placeholder="Ej: Joaquín / Personal 2026" autocomplete="off">
        </div>

        <button class="btn btn-green" onclick="irAArchivosPersona()">📊 Abrir Hoja de Cálculo</button>
        <button class="btn btn-outline" style="color: var(--accent-red);" onclick="cerrarSesion()">🚪 Cerrar Sesión</button>
      </div>
    </div>
  </div>

  <!-- HOJA DE CÁLCULO GIGANTE FULLSCREEN -->
  <div class="excel-app" id="vista-panel">
    <!-- RIBBON -->
    <header class="excel-ribbon">
      <div class="excel-title-area">
        <span class="excel-logo">XLS</span>
        <span class="excel-doc-title">Planilla_Gastos_<span id="badge-usuario">Persona</span>.xlsx</span>
      </div>
      <div>
        <button class="btn btn-outline btn-sm" onclick="volverAInicio()" style="background: white; border: none; padding: 0.3rem 0.8rem; font-size: 0.8rem;">🏠 Volver</button>
      </div>
    </header>

    <!-- TOOLBAR DE ACCIONES -->
    <div class="excel-toolbar">
      <div class="toolbar-group">
        <span class="toolbar-label">Ingresar Registro:</span>
        <input type="date" id="input-fecha" class="input-sm">
        <select id="select-categoria" class="input-sm"></select>
        <input type="text" id="input-concepto" placeholder="Concepto / Detalle" class="input-sm" style="width: 180px;">
        <input type="text" id="input-monto" placeholder="Monto ($)" class="input-sm" style="width: 100px;">
        <button class="btn btn-green" onclick="agregarGastoFila(event)" style="padding: 0.3rem 0.8rem; font-size: 0.85rem;">+ Agregar Fila</button>
      </div>

      <div class="toolbar-group" style="margin-left: auto;">
        <span class="toolbar-label">Nueva Categoría:</span>
        <input type="text" id="input-nueva-cat" placeholder="Categoría" class="input-sm" style="width: 110px;">
        <button class="btn btn-outline" onclick="crearNuevaCategoria(event)" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;">+ Crear</button>
      </div>
    </div>

    <!-- RESUMEN DE SALDOS -->
    <div class="excel-summary-bar">
      <div class="stat-box">
        <span class="lbl">Ingresos Totales</span>
        <div class="val" id="val-ingresos" style="color: var(--excel-green); cursor: pointer;" onclick="modificarIngreso()" title="Clic para modificar">$0,00 ✏️</div>
      </div>
      <div class="stat-box">
        <span class="lbl">Gastos Totales</span>
        <div class="val" id="val-gastos" style="color: var(--accent-red);">$0,00</div>
      </div>
      <div class="stat-box">
        <span class="lbl">Saldo Restante</span>
        <div class="val" id="val-balance">$0,00</div>
      </div>
    </div>

    <!-- BARRA DE FÓRMULAS -->
    <div class="formula-bar">
      <div class="cell-name-box" id="active-cell-id">A1</div>
      <div class="fx-btn">fx</div>
      <div class="formula-input-container">
        <input type="text" id="formula-input" placeholder="Contenido de la celda activa..." readonly>
      </div>
    </div>

    <!-- GRILLA COMPLETA -->
    <div class="grid-container">
      <table class="excel-grid">
        <thead>
          <tr>
            <th class="col-row-num">#</th>
            <th style="width: 50px;">Move</th>
            <th style="width: 130px;">A - Fecha</th>
            <th style="width: 180px;">B - Categoría</th>
            <th>C - Concepto / Descripción</th>
            <th style="width: 180px; text-align: right;">D - Monto ($)</th>
            <th style="width: 60px;">Acción</th>
          </tr>
        </thead>
        <tbody id="tbody-excel">
        </tbody>
      </table>
    </div>

    <!-- PESTAÑAS INFERIORES -->
    <footer class="excel-bottom-bar">
      <div class="excel-tabs">
        <div class="excel-tab active">Hoja 1 - Movimientos</div>
      </div>
      <div>
        <span>Listo | Modo Edición Directa</span>
      </div>
    </footer>
  </div>

  <script>
    let modoRegistro = false;
    let usuarioActual = null;
    let nombreUsuarioClave = '';
    let datosUsuario = { ingresos: 0, categorias: ['Servicios', 'Alquiler', 'Comida', 'Varios'], listaGastos: [] };

    function alternarModoAuth() {
      modoRegistro = !modoRegistro;
      document.getElementById('auth-titulo').innerText = modoRegistro ? 'Crear Cuenta' : 'Iniciar Sesión';
      document.getElementById('auth-btn-submit').innerText = modoRegistro ? 'Registrarse' : 'Entrar al Sistema';
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
        alert('Cuenta creada. Inicia sesión.');
        alternarModoAuth();
      } else {
        if (!usuarios[email] || usuarios[email].password !== pass) return alert('Credenciales incorrectas.');
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
      return 'usuario_gastos_' + usuarioActual + '_' + nombreUsuarioClave;
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
      if (!inputNom) return alert('Ingresa un nombre para continuar.');
      
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
      if (e) e.preventDefault();
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
      if (e) e.preventDefault();
      const fecha = document.getElementById('input-fecha').value;
      const categoria = document.getElementById('select-categoria').value;
      const concepto = document.getElementById('input-concepto').value.trim();
      const monto = parsearMontoFlexible(document.getElementById('input-monto').value);

      datosUsuario.listaGastos.unshift({ id: Date.now(), fecha: fecha, categoria: categoria, concepto: concepto, monto: monto });
      guardarDatosUsuario();
      actualizarPantallaPanel();

      document.getElementById('input-concepto').value = '';
      document.getElementById('input-monto').value = '';
    }

    function modificarIngreso() {
      const nuevoIngreso = prompt('Ingresa el monto de Ingresos:', datosUsuario.ingresos);
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

      document.getElementById('val-ingresos').innerText = formatearMoneda(datosUsuario.ingresos) + ' ✏️';
      document.getElementById('val-gastos').innerText = formatearMoneda(totalGastos);

      const balance = datosUsuario.ingresos - totalGastos;
      const valBalanceElem = document.getElementById('val-balance');
      valBalanceElem.innerText = formatearMoneda(balance);
      valBalanceElem.style.color = balance < 0 ? 'var(--accent-red)' : 'var(--excel-green)';

      renderTablaExcel();
    }

    function renderTablaExcel() {
      const tbody = document.getElementById('tbody-excel');
      tbody.innerHTML = '';

      const minRows = Math.max(25, datosUsuario.listaGastos.length + 5);

      for (let i = 0; i < minRows; i++) {
        const item = datosUsuario.listaGastos[i];
        const tr = document.createElement('tr');

        if (item) {
          tr.draggable = true;
          tr.dataset.index = i;

          let catOptionsHTML = datosUsuario.categorias.map(c => 
            '<option value="' + c + '" ' + (c === item.categoria ? 'selected' : '') + '>' + c + '</option>'
          ).join('');

          tr.innerHTML = `
            <td class="row-num">${i + 1}</td>
            <td class="drag-handle">≡</td>
            <td>
              <input type="date" value="${item.fecha}" style="border:none; background:transparent; font-family:inherit; width:100%;" onchange="actualizarCelda(${item.id}, 'fecha', this.value)" onfocus="setFormula('A${i+1}', this.value)">
            </td>
            <td>
              <select style="border:none; background:transparent; font-weight:bold; color: var(--excel-green); width:100%;" onchange="actualizarCelda(${item.id}, 'categoria', this.value)" onfocus="setFormula('B${i+1}', this.value)">
                ${catOptionsHTML}
              </select>
            </td>
            <td contenteditable="true" onfocus="setFormula('C${i+1}', this.innerText)" onblur="actualizarCelda(${item.id}, 'concepto', this.innerText)">${item.concepto}</td>
            <td contenteditable="true" style="text-align: right; font-weight: 700; color: var(--accent-red);" onfocus="setFormula('D${i+1}', this.innerText)" onblur="actualizarCeldaMonto(${item.id}, this.innerText)">
              ${formatearMoneda(item.monto)}
            </td>
            <td style="text-align: center;">
              <button style="border:none; background:none; cursor:pointer; color:var(--accent-red);" onclick="eliminarFila(${item.id})">🗑️</button>
            </td>
          `;

          tr.addEventListener('dragstart', handleDragStart);
          tr.addEventListener('dragover', handleDragOver);
          tr.addEventListener('drop', handleDrop);
          tr.addEventListener('dragend', handleDragEnd);

        } else {
          tr.innerHTML = `
            <td class="row-num">${i + 1}</td>
            <td></td>
            <td contenteditable="true" onfocus="setFormula('A${i+1}', '')"></td>
            <td contenteditable="true" onfocus="setFormula('B${i+1}', '')"></td>
            <td contenteditable="true" onfocus="setFormula('C${i+1}', '')"></td>
            <td contenteditable="true" onfocus="setFormula('D${i+1}', '')"></td>
            <td></td>
          `;
        }

        tbody.appendChild(tr);
      }
    }

    function setFormula(cellId, val) {
      document.getElementById('active-cell-id').innerText = cellId;
      document.getElementById('formula-input').value = val;
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

    let dragSrcIndex = null;
    function handleDragStart(e) { dragSrcIndex = this.dataset.index; this.classList.add('dragging'); }
    function handleDragOver(e) { if (e.preventDefault) e.preventDefault(); return false; }
    function handleDrop(e) {
      if (e.stopPropagation) e.stopPropagation();
      const targetIndex = this.dataset.index;
      if (dragSrcIndex !== null && targetIndex !== undefined && dragSrcIndex !== targetIndex) {
        const elementoMovido = datosUsuario.listaGastos.splice(dragSrcIndex, 1)[0];
        if (elementoMovido) {
          datosUsuario.listaGastos.splice(targetIndex, 0, elementoMovido);
          guardarDatosUsuario();
          actualizarPantallaPanel();
        }
      }
      return false;
    }
    function handleDragEnd() { this.classList.remove('dragging'); }
  </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CONTENT)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)