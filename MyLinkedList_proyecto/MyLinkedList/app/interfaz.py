"""
Interfaz gráfica completa para MyLinkedList.

Novedades:
  • Nodos vacíos (dato = ∅)
  • Panel de métodos: Recorrido / Inserción / Borrado / Búsqueda
  • Botón "Generar árbol" que puebla automáticamente la lista
  • Modo de enlace intuitivo: clic en nodo origen → clic en nodo destino
  • Arrastrar nodos con el ratón (fuera del modo enlace)
"""

import math
import random
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from MyLinkedList import ListaLigada

# ──────────────────────────────────────────────────────────────
#  Paleta de colores
# ──────────────────────────────────────────────────────────────
BG_APP      = "#1e1e2e"
BG_PANEL    = "#2a2a3e"
BG_CANVAS   = "#12121c"
FG_TEXT     = "#cdd6f4"
FG_MUTED    = "#7f849c"
ACCENT      = "#89b4fa"
ACCENT2     = "#cba6f7"
OK_COLOR    = "#a6e3a1"
WARN_COLOR  = "#fab387"
ERR_COLOR   = "#f38ba8"
LINK_COLOR  = "#f9e2af"   # amarillo modo enlace

NODE_FILL_NORMAL   = "#313244"
NODE_FILL_EMPTY    = "#45475a"   # nodo vacio
NODE_FILL_HEAD     = "#1e66f5"
NODE_FILL_TAIL     = "#179299"
NODE_FILL_SELECTED = "#e64553"
NODE_FILL_FOUND    = "#40a02b"
NODE_FILL_LINKING  = "#f9e2af"   # origen en modo enlace
NODE_STROKE        = "#89b4fa"
NODE_RADIUS        = 34

ARROW_MAIN   = "#89b4fa"
ARROW_EXTRA  = "#cba6f7"
ARROW_WIDTH  = 2

DATO_VACIO = "\u2205"   # simbolo de conjunto vacio


class Aplicacion:
    """Ventana principal de MyLinkedList con panel + canvas."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MyLinkedList – Visualizador de Lista Ligada")
        self.root.geometry("1400x780")
        self.root.configure(bg=BG_APP)
        self.root.minsize(1000, 640)

        self.lista = ListaLigada()

        # Estado de UI
        self._posiciones: dict[int, list[float]] = {}   # id → [cx, cy]
        self._seleccionado: int | None = None
        self._resaltado: set[int] = set()                # IDs con highlight
        self._drag_id: int | None = None
        self._drag_dx = 0.0
        self._drag_dy = 0.0

        # Modo enlace: clic-clic para conectar nodos en el canvas
        self._modo_enlace = False
        self._enlace_origen: int | None = None

        self._construir_ui()
        self._actualizar_todo()

    # ──────────────────────────────────────────────────────────
    #  Construcción de la interfaz
    # ──────────────────────────────────────────────────────────

    def _construir_ui(self):
        # Encabezado
        hdr = tk.Frame(self.root, bg=BG_APP, pady=8)
        hdr.pack(fill="x", padx=16)
        tk.Label(
            hdr, text="⛓  MyLinkedList",
            font=("Segoe UI", 20, "bold"),
            fg=ACCENT, bg=BG_APP
        ).pack(side="left")
        tk.Label(
            hdr, text="Visualizador interactivo de lista ligada",
            font=("Segoe UI", 10),
            fg=FG_MUTED, bg=BG_APP
        ).pack(side="left", padx=12)

        # Separador
        tk.Frame(self.root, bg=ACCENT, height=1).pack(fill="x", padx=0)

        # Cuerpo principal: panel izquierdo + canvas derecho
        cuerpo = tk.Frame(self.root, bg=BG_APP)
        cuerpo.pack(fill="both", expand=True, padx=0, pady=0)

        self._construir_panel(cuerpo)
        self._construir_canvas(cuerpo)

    # ── Panel izquierdo ───────────────────────────────────────

    def _construir_panel(self, padre):
        panel = tk.Frame(padre, bg=BG_PANEL, width=340)
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)

        # Scrollable interior
        cs = tk.Canvas(panel, bg=BG_PANEL, highlightthickness=0)
        sb_v = tk.Scrollbar(panel, orient="vertical", command=cs.yview)
        cs.configure(yscrollcommand=sb_v.set)
        sb_v.pack(side="right", fill="y")
        cs.pack(side="left", fill="both", expand=True)

        interior = tk.Frame(cs, bg=BG_PANEL)
        win_id = cs.create_window((0, 0), window=interior, anchor="nw")

        cs.bind("<Configure>", lambda e: cs.itemconfig(win_id, width=e.width))
        interior.bind("<Configure>",
                      lambda e: cs.configure(scrollregion=cs.bbox("all")))

        self._rellenar_panel(interior)

    def _rellenar_panel(self, p):
        pad = dict(padx=12, pady=3)

        # ══ INSERCION ════════════════════════════════════════
        self._seccion(p, "\u2795  Inserci\u00f3n")

        tk.Label(p, text="Dato del nodo:", font=("Segoe UI", 9),
                 fg=FG_MUTED, bg=BG_PANEL).pack(anchor="w", padx=14)

        self._var_entrada = tk.StringVar()
        entry = tk.Entry(
            p, textvariable=self._var_entrada,
            font=("Segoe UI", 11),
            bg="#313244", fg=FG_TEXT,
            insertbackground=FG_TEXT, relief="flat", bd=6
        )
        entry.pack(fill="x", **pad)
        entry.bind("<Return>", lambda _e: self._insertar())

        bf1 = tk.Frame(p, bg=BG_PANEL)
        bf1.pack(fill="x", **pad)
        self._btn(bf1, "Al final",  ACCENT,  self._insertar).pack(
            side="left", fill="x", expand=True, padx=(0, 3))
        self._btn(bf1, "Al inicio", ACCENT2, self._insertar_inicio).pack(
            side="left", fill="x", expand=True, padx=(3, 0))

        self._btn(p, "Insertar en posici\u00f3n\u2026", ACCENT,
                  self._insertar_posicion).pack(fill="x", **pad)
        self._btn(p, "\U0001fad9  Insertar nodo vac\u00edo (\u2205)", NODE_FILL_EMPTY,
                  self._insertar_vacio).pack(fill="x", **pad)

        # ══ BORRADO ═══════════════════════════════════════════
        self._seccion(p, "\U0001f5d1  Borrado")
        self._btn(p, "Eliminar nodo seleccionado", ERR_COLOR,
                  self._eliminar).pack(fill="x", **pad)
        self._btn(p, "\U0001f9f9  Limpiar toda la lista", ERR_COLOR,
                  self._limpiar).pack(fill="x", **pad)

        # ══ BUSQUEDA ══════════════════════════════════════════
        self._seccion(p, "\U0001f50d  B\u00fasqueda")
        tk.Label(p, text="Dato a buscar:", font=("Segoe UI", 9),
                 fg=FG_MUTED, bg=BG_PANEL).pack(anchor="w", padx=14)
        self._var_busqueda = tk.StringVar()
        tk.Entry(
            p, textvariable=self._var_busqueda,
            font=("Segoe UI", 11),
            bg="#313244", fg=FG_TEXT,
            insertbackground=FG_TEXT, relief="flat", bd=6
        ).pack(fill="x", **pad)
        self._btn(p, "Buscar dato", OK_COLOR, self._buscar).pack(fill="x", **pad)

        # ══ RECORRIDO ═════════════════════════════════════════
        self._seccion(p, "\U0001f6b6  Recorrido")
        self._btn(p, "Recorrer desde cabeza", ACCENT,
                  self._recorrer).pack(fill="x", **pad)
        self._btn(p, "Recorrer desde nodo sel.", ACCENT2,
                  self._recorrer_desde).pack(fill="x", **pad)

        # ══ CONEXIONES ════════════════════════════════════════
        self._seccion(p, "\U0001f517  Conexiones (\u00e1rbol)")

        self._var_modo_enlace = tk.StringVar(value="\U0001f517  Modo enlace: OFF")
        self._btn_enlace = tk.Button(
            p,
            textvariable=self._var_modo_enlace,
            font=("Segoe UI", 10, "bold"),
            bg=BG_PANEL, fg=LINK_COLOR,
            activebackground=LINK_COLOR, activeforeground="#1e1e2e",
            relief="flat", bd=0, padx=10, pady=6,
            cursor="hand2",
            command=self._toggle_modo_enlace,
            highlightbackground=LINK_COLOR,
            highlightthickness=1
        )
        self._btn_enlace.pack(fill="x", **pad)

        tk.Label(
            p,
            text="Activa el modo enlace y haz\nclic en origen \u2192 destino en el canvas.",
            font=("Segoe UI", 8), fg=FG_MUTED, bg=BG_PANEL, justify="left"
        ).pack(anchor="w", padx=14)

        self._btn(p, "\u2702\ufe0f  Eliminar enlace extra", WARN_COLOR,
                  self._eliminar_enlace).pack(fill="x", **pad)

        # ══ GENERAR ARBOL ══════════════════════════════════════
        self._seccion(p, "\U0001f333  Generar \u00e1rbol")

        tk.Label(p, text="Tipo:", font=("Segoe UI", 9),
                 fg=FG_MUTED, bg=BG_PANEL).pack(anchor="w", padx=14)
        self._var_tipo_arbol = tk.StringVar(value="Binario")
        combo = ttk.Combobox(
            p, textvariable=self._var_tipo_arbol,
            values=["Binario", "Lineal", "Estrella", "Aleatorio"],
            state="readonly", font=("Segoe UI", 10)
        )
        combo.pack(fill="x", **pad)

        bf2 = tk.Frame(p, bg=BG_PANEL)
        bf2.pack(fill="x", **pad)
        tk.Label(bf2, text="Nodos:", font=("Segoe UI", 9),
                 fg=FG_MUTED, bg=BG_PANEL).pack(side="left")
        self._var_n_arbol = tk.StringVar(value="7")
        tk.Entry(bf2, textvariable=self._var_n_arbol, width=5,
                 font=("Segoe UI", 10), bg="#313244", fg=FG_TEXT,
                 insertbackground=FG_TEXT, relief="flat", bd=4).pack(
            side="left", padx=6)

        self._btn(p, "\U0001f333  Generar \u00e1rbol", OK_COLOR,
                  self._generar_arbol).pack(fill="x", **pad)

        # ══ LISTA DE NODOS ═════════════════════════════════════
        self._seccion(p, "\U0001f4cb  Nodos en la lista")

        lista_frame = tk.Frame(p, bg=BG_PANEL)
        lista_frame.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        scrollbar = tk.Scrollbar(lista_frame, bg=BG_PANEL)
        scrollbar.pack(side="right", fill="y")

        self._listbox = tk.Listbox(
            lista_frame,
            font=("Consolas", 10),
            bg="#313244", fg=FG_TEXT,
            selectbackground=ACCENT,
            selectforeground="#1e1e2e",
            relief="flat", bd=0,
            activestyle="none",
            yscrollcommand=scrollbar.set
        )
        self._listbox.pack(fill="both", expand=True)
        self._listbox.bind("<<ListboxSelect>>", self._seleccionar_nodo)
        scrollbar.config(command=self._listbox.yview)

        self._lbl_estado = tk.Label(
            p, text="Lista vac\u00eda",
            font=("Segoe UI", 9), fg=FG_MUTED, bg=BG_PANEL
        )
        self._lbl_estado.pack(anchor="w", padx=16, pady=(4, 10))

    def _seccion(self, padre, titulo):
        """Dibuja separador + titulo de seccion."""
        tk.Frame(padre, bg="#45475a", height=1).pack(fill="x", padx=8, pady=(10, 0))
        tk.Label(
            padre, text=titulo,
            font=("Segoe UI", 10, "bold"),
            fg=ACCENT, bg=BG_PANEL
        ).pack(anchor="w", padx=14, pady=(4, 2))

    @staticmethod
    def _btn(padre, texto, color, comando):
        return tk.Button(
            padre, text=texto,
            font=("Segoe UI", 10, "bold"),
            bg=color, fg="#1e1e2e",
            activebackground=color,
            activeforeground="#1e1e2e",
            relief="flat", bd=0, padx=10, pady=6,
            cursor="hand2",
            command=comando
        )

    # ── Canvas derecho ────────────────────────────────────────

    def _construir_canvas(self, padre):
        canvas_frame = tk.Frame(padre, bg=BG_CANVAS)
        canvas_frame.pack(side="left", fill="both", expand=True)

        # Barra de herramientas del canvas
        toolbar = tk.Frame(canvas_frame, bg=BG_PANEL, height=36)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        tk.Label(
            toolbar, text="  📐 Árbol / Grafo interactivo — arrastra los nodos con el ratón",
            font=("Segoe UI", 9), fg=FG_MUTED, bg=BG_PANEL
        ).pack(side="left", pady=6)

        self._btn(toolbar, "⟳ Reorganizar", ACCENT, self._reorganizar).pack(
            side="right", padx=8, pady=4
        )

        self._canvas = tk.Canvas(
            canvas_frame,
            bg=BG_CANVAS,
            highlightthickness=0
        )
        self._canvas.pack(fill="both", expand=True)

        # Eventos del canvas
        self._canvas.bind("<ButtonPress-1>",   self._canvas_click)
        self._canvas.bind("<B1-Motion>",        self._canvas_drag)
        self._canvas.bind("<ButtonRelease-1>",  self._canvas_release)

        # Leyenda
        leyenda = tk.Frame(canvas_frame, bg=BG_CANVAS)
        leyenda.pack(fill="x", padx=12, pady=4)
        for color, texto in [
            (NODE_FILL_HEAD,     "Cabeza"),
            (NODE_FILL_TAIL,     "Cola"),
            (NODE_FILL_SELECTED, "Seleccionado"),
            (NODE_FILL_FOUND,    "Encontrado"),
            (ARROW_MAIN,         "Enlace principal"),
            (ARROW_EXTRA,        "Enlace extra"),
        ]:
            dot = tk.Canvas(leyenda, width=12, height=12, bg=BG_CANVAS, highlightthickness=0)
            dot.create_oval(1, 1, 11, 11, fill=color, outline="")
            dot.pack(side="left", padx=(8, 2))
            tk.Label(leyenda, text=texto, font=("Segoe UI", 8),
                     fg=FG_MUTED, bg=BG_CANVAS).pack(side="left", padx=(0, 8))

    # ──────────────────────────────────────────────────────────
    #  Operaciones sobre la lista
    # ──────────────────────────────────────────────────────────

    def _insertar(self):
        dato = self._var_entrada.get().strip()
        if not dato:
            messagebox.showwarning("Dato requerido", "Escribe un dato para insertar.")
            return
        self.lista.insertar(dato)
        self._var_entrada.set("")
        self._actualizar_todo()

    def _insertar_inicio(self):
        dato = self._var_entrada.get().strip()
        if not dato:
            messagebox.showwarning("Dato requerido", "Escribe un dato para insertar.")
            return
        self.lista.insertar(dato, 0)
        self._var_entrada.set("")
        self._actualizar_todo()

    def _eliminar(self):
        sel = self._listbox.curselection()
        if not sel:
            messagebox.showinfo("Selecciona un nodo",
                                "Haz clic en un nodo de la lista o en el canvas.")
            return
        nodo = self.lista.obtener_posicion(sel[0])
        if nodo is not None:
            self._posiciones.pop(nodo.id, None)
            self.lista.eliminar(nodo.id)
            self._seleccionado = None
            self._resaltado.discard(nodo.id)
            self._actualizar_todo()

    def _buscar(self):
        dato = self._var_entrada.get().strip()
        if not dato:
            messagebox.showwarning("Dato requerido", "Escribe el dato que deseas buscar.")
            return
        self._resaltado.clear()
        nodo = self.lista.buscar(dato)
        if nodo is None:
            messagebox.showinfo("Búsqueda", f"No se encontró: «{dato}»")
        else:
            self._resaltado.add(nodo.id)
            messagebox.showinfo("Búsqueda",
                                f"✔ Encontrado: «{nodo.dato}»  (ID {nodo.id})")
        self._dibujar_canvas()

    def _insertar_posicion(self):
        dato = self._var_entrada.get().strip()
        if not dato:
            messagebox.showwarning("Dato requerido", "Escribe un dato para insertar.")
            return
        posicion = simpledialog.askinteger(
            "Insertar en posición",
            "Indica el índice donde quieres insertarlo:",
            parent=self.root,
            minvalue=0,
            maxvalue=max(0, len(self.lista))
        )
        if posicion is None:
            return
        self.lista.insertar(dato, posicion)
        self._var_entrada.set("")
        self._actualizar_todo()

    def _insertar_vacio(self):
        self.lista.insertar(DATO_VACIO)
        self._actualizar_todo()

    def _recorrer_desde(self):
        sel = self._listbox.curselection()
        if sel:
            nodo = self.lista.obtener_posicion(sel[0])
            inicio = nodo.id if nodo else None
        else:
            inicio = getattr(self.lista.cabeza, "id", None)

        visitados = self.lista.recorrer(inicio)
        self._resaltado = {n.id for n in visitados}
        ruta = " → ".join(f"[{n.id}]{n.dato}" for n in visitados)
        messagebox.showinfo(
            "Recorrido",
            f"Recorrido desde {inicio if inicio is not None else 'inicio'} ({len(visitados)} nodos):\n{ruta}"
            if ruta else "La lista está vacía."
        )
        self._dibujar_canvas()

    def _toggle_modo_enlace(self):
        self._modo_enlace = not self._modo_enlace
        self._enlace_origen = None
        self._var_modo_enlace.set(
            "🔗  Modo enlace: ON" if self._modo_enlace else "🔗  Modo enlace: OFF"
        )
        self._dibujar_canvas()

    def _generar_arbol(self):
        self.lista.limpiar()
        tipo = self._var_tipo_arbol.get()
        total = self._var_n_arbol.get().strip()
        try:
            total = max(1, int(total))
        except ValueError:
            messagebox.showwarning("Número inválido", "Introduce un número entero válido de nodos.")
            return

        if tipo == "Lineal":
            for i in range(total):
                self.lista.insertar(f"N{i + 1}")
        elif tipo == "Binario":
            for i in range(total):
                self.lista.insertar(f"{chr(65 + (i % 26))}{i + 1}")
        elif tipo == "Estrella":
            for i in range(total):
                et = "*" if i == 0 else str(i)
                self.lista.insertar(f"{et}")
        else:
            for i in range(total):
                self.lista.insertar(f"v{i + 1}")

        self._posiciones.clear()
        self._seleccionado = None
        self._resaltado.clear()
        self._actualizar_todo()

    def _agregar_enlace(self):
        ids = sorted(n.id for n in self.lista)
        if len(ids) < 2:
            messagebox.showwarning("Pocos nodos", "Necesitas al menos 2 nodos.")
            return
        origen  = simpledialog.askinteger("Agregar enlace",
                                          f"ID de origen   (disponibles: {ids}):",
                                          parent=self.root)
        if origen is None:
            return
        destino = simpledialog.askinteger("Agregar enlace",
                                          f"ID de destino  (disponibles: {ids}):",
                                          parent=self.root)
        if destino is None:
            return
        try:
            self.lista.agregar_enlace(origen, destino)
            self._actualizar_todo()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _eliminar_enlace(self):
        extra = list(self.lista.enlaces_extra)
        if not extra:
            messagebox.showinfo("Sin enlaces extra", "No hay enlaces extra para eliminar.")
            return
        origen  = simpledialog.askinteger("Eliminar enlace",
                                          f"ID de origen del enlace extra:",
                                          parent=self.root)
        if origen is None:
            return
        destino = simpledialog.askinteger("Eliminar enlace",
                                          f"ID de destino del enlace extra:",
                                          parent=self.root)
        if destino is None:
            return
        eliminado = self.lista.eliminar_enlace(origen, destino)
        if eliminado:
            self._actualizar_todo()
        else:
            messagebox.showwarning("No encontrado",
                                   f"No existe el enlace extra {origen} → {destino}.")

    def _recorrer(self):
        visitados = self.lista.recorrer()
        self._resaltado = {n.id for n in visitados}
        ruta = " → ".join(f"[{n.id}]{n.dato}" for n in visitados)
        messagebox.showinfo("Recorrido",
                            f"Recorrido ({len(visitados)} nodos):\n{ruta}" if ruta
                            else "La lista está vacía.")
        self._dibujar_canvas()

    def _limpiar(self):
        if not messagebox.askyesno("Limpiar",
                                   "¿Eliminar todos los nodos y enlaces?"):
            return
        self.lista.limpiar()
        self._posiciones.clear()
        self._seleccionado = None
        self._resaltado.clear()
        self._actualizar_todo()

    # ──────────────────────────────────────────────────────────
    #  Selección desde listbox
    # ──────────────────────────────────────────────────────────

    def _seleccionar_nodo(self, _event=None):
        sel = self._listbox.curselection()
        if not sel:
            return
        nodo = self.lista.obtener_posicion(sel[0])
        if nodo:
            self._seleccionado = nodo.id
            self._resaltado.clear()
            self._dibujar_canvas()

    # ──────────────────────────────────────────────────────────
    #  Actualización general
    # ──────────────────────────────────────────────────────────

    def _actualizar_todo(self):
        # Asignar posiciones a nodos nuevos
        self._asignar_posiciones()

        # Listbox
        self._listbox.delete(0, tk.END)
        for nodo in self.lista:
            prefijo = ""
            if self.lista.cabeza and nodo.id == self.lista.cabeza.id:
                prefijo = "▶ "
            if self.lista.cola and nodo.id == self.lista.cola.id:
                prefijo = prefijo or "◀ "
            self._listbox.insert(tk.END, f"{prefijo}ID {nodo.id}: {nodo.dato}")

        # Estado
        n = len(self.lista)
        self._lbl_estado.config(
            text=f"{n} nodo{'s' if n != 1 else ''}  |  "
                 f"Cabeza: {self.lista.cabeza.id if self.lista.cabeza else '—'}  |  "
                 f"Cola: {self.lista.cola.id if self.lista.cola else '—'}"
        )

        self._dibujar_canvas()

    # ──────────────────────────────────────────────────────────
    #  Posiciones en el canvas
    # ──────────────────────────────────────────────────────────

    def _asignar_posiciones(self):
        """Asigna posición inicial a nodos nuevos; no mueve los ya existentes."""
        nodos = list(self.lista)
        conocidos = set(self._posiciones.keys())
        nuevos = [n for n in nodos if n.id not in conocidos]

        if not nuevos:
            return

        w = self._canvas.winfo_width()  or 900
        h = self._canvas.winfo_height() or 500
        cx, cy = w // 2, h // 2

        total = len(nodos)
        for i, nodo in enumerate(nodos):
            if nodo.id not in self._posiciones:
                # Disposición en árbol horizontal con jitter
                nivel = i
                angulo = (2 * math.pi * nivel / max(total, 1))
                radio  = min(w, h) * 0.35
                x = cx + radio * math.cos(angulo) + random.uniform(-20, 20)
                y = cy + radio * math.sin(angulo) + random.uniform(-20, 20)
                self._posiciones[nodo.id] = [x, y]

    def _reorganizar(self):
        """Redistribuye los nodos en árbol jerárquico."""
        nodos = list(self.lista)
        if not nodos:
            return

        w = self._canvas.winfo_width()  or 900
        h = self._canvas.winfo_height() or 500

        # Árbol: distribución de niveles
        # Los nodos de la cadena principal forman el tronco (eje horizontal)
        # Los enlaces extra se toman en cuenta para acomodar hijos.

        # Paso 1: construir grafo de adyacencia con todos los enlaces
        grafo: dict[int, list[int]] = {n.id: [] for n in nodos}
        for origen, destino in self.lista.todos_los_enlaces():
            if destino in grafo:
                grafo[origen].append(destino)

        # Paso 2: BFS desde la cabeza
        raiz = self.lista.cabeza
        if raiz is None:
            return

        visitados: set[int] = set()
        niveles: dict[int, list[int]] = {}
        cola: list[tuple[int, int]] = [(raiz.id, 0)]
        visitados.add(raiz.id)

        while cola:
            nid, nivel = cola.pop(0)
            niveles.setdefault(nivel, []).append(nid)
            for hijo in grafo.get(nid, []):
                if hijo not in visitados:
                    visitados.add(hijo)
                    cola.append((hijo, nivel + 1))

        # Nodos desconectados (sin llegar desde la cabeza)
        max_nivel = max(niveles.keys(), default=0)
        for n in nodos:
            if n.id not in visitados:
                max_nivel += 1
                niveles[max_nivel] = [n.id]

        # Paso 3: asignar coordenadas
        num_niveles = len(niveles)
        paso_x = w / (num_niveles + 1)

        for nivel, ids in niveles.items():
            x = paso_x * (nivel + 1)
            paso_y = h / (len(ids) + 1)
            for j, nid in enumerate(ids):
                y = paso_y * (j + 1)
                self._posiciones[nid] = [x, y]

        self._dibujar_canvas()

    # ──────────────────────────────────────────────────────────
    #  Dibujo del canvas
    # ──────────────────────────────────────────────────────────

    def _dibujar_canvas(self):
        c = self._canvas
        c.delete("all")

        nodos = list(self.lista)
        if not nodos:
            c.create_text(
                c.winfo_width() // 2 or 450,
                c.winfo_height() // 2 or 250,
                text="Lista vacía\n\nInserta un nodo para comenzar",
                font=("Segoe UI", 14), fill=FG_MUTED, justify="center"
            )
            return

        # Asegurar posiciones antes de dibujar
        self._asignar_posiciones()

        # ── Dibujar aristas ──────────────────────────────────
        enlaces_principales = self.lista.enlaces_cadena()
        enlaces_extra        = self.lista.enlaces_extra

        for (oid, did), es_extra in [
            *[(e, False) for e in enlaces_principales],
            *[(e, True)  for e in enlaces_extra],
        ]:
            if oid not in self._posiciones or did not in self._posiciones:
                continue
            x1, y1 = self._posiciones[oid]
            x2, y2 = self._posiciones[did]
            color = ARROW_EXTRA if es_extra else ARROW_MAIN
            dash  = (6, 3) if es_extra else ()
            self._dibujar_flecha(c, x1, y1, x2, y2, color, dash)

        # ── Dibujar nodos ────────────────────────────────────
        for nodo in nodos:
            if nodo.id not in self._posiciones:
                continue
            x, y = self._posiciones[nodo.id]
            r = NODE_RADIUS

            # Color según estado
            if nodo.id == self._seleccionado:
                fill = NODE_FILL_SELECTED
            elif nodo.id in self._resaltado:
                fill = NODE_FILL_FOUND
            elif self.lista.cabeza and nodo.id == self.lista.cabeza.id:
                fill = NODE_FILL_HEAD
            elif self.lista.cola and nodo.id == self.lista.cola.id:
                fill = NODE_FILL_TAIL
            else:
                fill = NODE_FILL_NORMAL

            # Sombra
            c.create_oval(
                x - r + 3, y - r + 3, x + r + 3, y + r + 3,
                fill="#000000", outline="", stipple="gray25"
            )
            # Círculo principal
            c.create_oval(
                x - r, y - r, x + r, y + r,
                fill=fill, outline=NODE_STROKE, width=2,
                tags=(f"nodo_{nodo.id}", "nodo")
            )
            # Etiqueta: dato
            dato_corto = str(nodo.dato)[:10]
            c.create_text(
                x, y - 6,
                text=dato_corto,
                font=("Segoe UI", 10, "bold"),
                fill=FG_TEXT,
                tags=(f"nodo_{nodo.id}", "nodo")
            )
            # Etiqueta: ID
            c.create_text(
                x, y + 10,
                text=f"ID:{nodo.id}",
                font=("Segoe UI", 8),
                fill=FG_MUTED,
                tags=(f"nodo_{nodo.id}", "nodo")
            )

            # Etiqueta flotante cabeza / cola
            if self.lista.cabeza and nodo.id == self.lista.cabeza.id:
                c.create_text(x, y - r - 10, text="CABEZA",
                              font=("Segoe UI", 7, "bold"), fill=NODE_FILL_HEAD)
            if self.lista.cola and nodo.id == self.lista.cola.id:
                c.create_text(x, y + r + 10, text="COLA",
                              font=("Segoe UI", 7, "bold"), fill=NODE_FILL_TAIL)

    def _dibujar_flecha(self, c, x1, y1, x2, y2, color, dash=()):
        """Dibuja una flecha entre dos nodos acortada en los extremos."""
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist < 1:
            return
        ux, uy = dx / dist, dy / dist

        # Recortar desde la orilla del círculo
        mx1 = x1 + ux * (NODE_RADIUS + 4)
        my1 = y1 + uy * (NODE_RADIUS + 4)
        mx2 = x2 - ux * (NODE_RADIUS + 4)
        my2 = y2 - uy * (NODE_RADIUS + 4)

        c.create_line(
            mx1, my1, mx2, my2,
            fill=color, width=ARROW_WIDTH,
            arrow=tk.LAST, arrowshape=(10, 12, 4),
            dash=dash, smooth=True
        )

    # ──────────────────────────────────────────────────────────
    #  Arrastre de nodos en el canvas
    # ──────────────────────────────────────────────────────────

    def _canvas_click(self, event):
        nid = self._nodo_en(event.x, event.y)
        if nid is None:
            self._drag_id = None
            return

        if self._modo_enlace:
            if self._enlace_origen is None:
                self._enlace_origen = nid
                self._seleccionado = nid
                self._resaltado = {nid}
                self._dibujar_canvas()
                return

            if self._enlace_origen == nid:
                self._enlace_origen = None
                self._resaltado.clear()
                self._dibujar_canvas()
                return

            try:
                self.lista.agregar_enlace(self._enlace_origen, nid)
                self._enlace_origen = None
                self._resaltado.clear()
                self._actualizar_todo()
            except ValueError as exc:
                messagebox.showerror("Error de enlace", str(exc))
                self._enlace_origen = None
                self._resaltado.clear()
            return

        self._drag_id = nid
        px, py = self._posiciones[nid]
        self._drag_dx = event.x - px
        self._drag_dy = event.y - py
        self._seleccionado = nid
        self._resaltado.clear()
        # Sincronizar listbox
        for i, n in enumerate(self.lista):
            if n.id == nid:
                self._listbox.selection_clear(0, tk.END)
                self._listbox.selection_set(i)
                self._listbox.see(i)
                break
        self._dibujar_canvas()

    def _canvas_drag(self, event):
        if self._drag_id is not None and self._drag_id in self._posiciones:
            self._posiciones[self._drag_id] = [
                event.x - self._drag_dx,
                event.y - self._drag_dy
            ]
            self._dibujar_canvas()

    def _canvas_release(self, _event):
        self._drag_id = None

    def _nodo_en(self, x, y) -> int | None:
        """Devuelve el ID del nodo que contiene el punto (x, y), o None."""
        for nid, (cx, cy) in self._posiciones.items():
            if math.hypot(x - cx, y - cy) <= NODE_RADIUS:
                return nid
        return None


# ──────────────────────────────────────────────────────────────
#  Punto de entrada autónomo (útil durante desarrollo)
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    Aplicacion(root)
    root.mainloop()
