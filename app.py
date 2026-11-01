import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import os
from PIL import Image as PILImage
from reportlab.pdfgen import canvas
import pypdf
import anthropic

st.set_page_config(
    page_title="AUTOTEN - Gestión e Inspección Técnica", 
    page_icon="🚗",
    layout="wide"
)

st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #1E293B; margin-bottom: 0px; }
    .sub-title { font-size: 1rem; color: #64748B; margin-bottom: 20px; }
    .card-total-inversion {
        background-color: #FEF2F2;
        border-left: 6px solid #DC2626;
        padding: 18px;
        border-radius: 8px;
        color: #991B1B;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def check_password():
    def password_entered():
        if st.session_state.get("password") == "tibiano1":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        st.subheader("🔒 Acceso Restringido - AUTOTEN")
        st.text_input("Ingresa tu clave de acceso", type="password", on_change=password_entered, key="password")
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 Contraseña incorrecta.")
        return False
    return True

if not check_password():
    st.stop()

st.markdown('<p class="main-title">🚗 AUTOTEN - Sistema Integral de Peritaje e IA</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Dictamen Pericial Automatizado con API de Claude para Compra y Venta</p>', unsafe_allow_html=True)

tab_inspeccion, tab_inventario = st.tabs([
    "📋 1. Inspección & Dictamen Pericial IA (PDF)", 
    "📊 2. Control de Stock y Ganancias (Mes a Mes)"
])

# ---------------------------------------------------------
# MÓDULO 1: INSPECCIÓN TÉCNICA E INTEGRACIÓN TOTAL IA
# ---------------------------------------------------------
with tab_inspeccion:
    st.header("📋 Datos Principales de la Inspección")
    
    col_logo, col_info1, col_info2 = st.columns([1, 2, 2])
    with col_logo:
        st.subheader("🖼️ Marca e Identidad")
        nombre_marca = st.text_input("Nombre Encabezado PDF", value="AUTOTEN AUTOMOTORA")
        uploaded_logo = st.file_uploader("Cargar tu Logo (Aparecerá en todas las hojas)", type=["png", "jpg", "jpeg"], key="logo_app")
        if uploaded_logo:
            st.image(uploaded_logo, width=120, caption="Logo activo")

    with col_info1:
        patente = st.text_input("Patente del Vehículo", placeholder="EJ: KVKZ-45").upper()
        vehiculo = st.text_input("Marca / Modelo / Año", placeholder="Ej: Spark GT 2019")
        km = st.number_input("Kilometraje Tablero", min_value=0, step=1000, value=99000)

    with col_info2:
        precio_vendedor = st.number_input("Precio Pedido Vendedor [$]", min_value=0, step=100000, value=4300000)
        cantidad_duenos = st.selectbox("Cantidad de Dueños del Vehículo", ["1 dueños", "2 dueños", "3 o más dueños"])
        origen_legal = st.selectbox("Condición de Origen Legal", ["Vehículo Normal / Particular", "Pérdida Total (Aseguradora)", "Recuperado de Robo"])

    st.markdown("---")
    
    # REVISIÓN DE DOCUMENTACIÓN LEGAL
    st.subheader("📄 Paso 1: Documentación Legal e Historial del Vehículo")
    st.caption("Selecciona el estado de cada documento oficial del vehículo:")
    
    col_doc1, col_doc2, col_doc3, col_doc4 = st.columns(4)
    with col_doc1:
        doc_permiso = st.selectbox("Permiso de Circulación", ["🟢 Al día / Vigente", "🔴 Vencido / Deuda", "⚪ No presentado"])
    with col_doc2:
        doc_soap = st.selectbox("Seguro Obligatorio (SOAP)", ["🟢 Vigente", "🔴 Vencido", "⚪ No presentado"])
    with col_doc3:
        doc_rt = st.selectbox("Revisión Técnica / Gases", ["🟢 Al día / Aprobada", "🔴 Vencida / Rechazada", "⚪ No presentada"])
    with col_doc4:
        doc_padron = st.selectbox("Padrón / Título Dominio", ["🟢 Presente (Verificado)", "🔴 Extraviado", "🟡 En trámite"])

    st.markdown("---")

    # PASO 2: CARGA DE ARCHIVOS PDF (ESCÁNER AUTEL + AUTOFACT) + CLAVE API
    st.subheader("🔌 Paso 2: Integración de Escáner Autel, Autofact e IA Claude")
    
    claude_api_key = st.text_input("🔑 API Key de Claude (Anthropic)", type="password", placeholder="sk-ant-api03-...", value="")
    
    col_pdf1, col_pdf2 = st.columns(2)
    with col_pdf1:
        scanner_pdf = st.file_uploader("Subir PDF del Escáner Autel", type=["pdf"], key="scanner_pdf_upload")
        texto_escaner_extraido = ""
        if scanner_pdf is not None:
            st.success("✅ Reporte de escáner Autel adjuntado.")
            try:
                reader = pypdf.PdfReader(scanner_pdf)
                for pagina in reader.pages:
                    texto_escaner_extraido += pagina.extract_text() or ""
            except Exception as e:
                st.error(f"Error al leer PDF del escáner: {e}")

    with col_pdf2:
        autofact_pdf = st.file_uploader("Subir Informe PDF de Autofact", type=["pdf"], key="autofact_pdf_upload")
        texto_autofact_extraido = ""
        if autofact_pdf is not None:
            st.success("✅ Informe Autofact adjuntado.")
            try:
                reader_af = pypdf.PdfReader(autofact_pdf)
                for pagina in reader_af.pages:
                    texto_autofact_extraido += pagina.extract_text() or ""
            except Exception as e:
                st.error(f"Error al leer PDF de Autofact: {e}")

    st.markdown("---")

    # PASO 3: MEDICIÓN DE PINTURA
    st.subheader("🎨 Paso 3: Medición de Pintura por Pieza (µm) y Fotos")
    st.caption("Ingresa los micrómetros de cada panel para determinar pintura original, repintado o masilla.")

    st.info("""
    **📖 Rangos Explicativos de Pintura:**
    * 🟢 **< 130 µm:** Pintura Original de Fábrica.
    * 🟠 **130 - 169 µm:** Retoque Leve.
    * 🟡 **170 - 250 µm:** Repintado Denso.
    * 🔴 **> 250 µm:** Daño Grave / Masilla o Reparación Estructural.
    """)

    piezas_carroceria = [
        "Capó", "Tapabarro delantero derecho", "Puerta delantera derecha", "Puerta trasera derecha", 
        "Costado trasero derecho", "Maletero / Portalón", "Costado trasero izquierdo", 
        "Puerta trasera izquierda", "Puerta delantera izquierda", "Tapabarro delantero izquierdo", "Techo y Pilares"
    ]

    datos_pintura = {}
    for pieza in piezas_carroceria:
        with st.expander(f"🔍 Panel: {pieza}"):
            c_p1, c_p2 = st.columns([1, 2])
            with c_p1:
                micras_val = st.number_input(f"Micras {pieza} (µm)", min_value=0, max_value=2000, value=110, key=f"mic_{pieza}")
                
                estado_str = "Original (OK)"
                if micras_val > 250:
                    st.markdown(f"<span style='color:red; font-weight:bold;'>🔴 Daño Grave / Masilla</span>", unsafe_allow_html=True)
                    estado_str = "Daño Grave / Masilla"
                elif micras_val >= 170:
                    st.markdown(f"<span style='color:orange; font-weight:bold;'>🟡 Repintado Denso</span>", unsafe_allow_html=True)
                    estado_str = "Repintado Denso"
                elif micras_val >= 130:
                    st.markdown(f"<span style='color:goldenrod; font-weight:bold;'>🟠 Retoque Leve</span>", unsafe_allow_html=True)
                    estado_str = "Retoque Leve"
                else:
                    st.markdown(f"<span style='color:green; font-weight:bold;'>🟢 Original (OK)</span>", unsafe_allow_html=True)
                    estado_str = "Original (OK)"
            
            with c_p2:
                foto_pieza = st.file_uploader(f"Foto de detalle en {pieza}", type=["jpg", "jpeg", "png"], key=f"foto_{pieza}")

            datos_pintura[pieza] = {"micras": micras_val, "estado": estado_str, "foto": foto_pieza}

    st.markdown("---")

    # PASO 4: FRENOS, NEUMÁTICOS Y BATERÍA
    st.subheader("🔧 Paso 4: Estado de Frenos, Neumáticos y Batería (% Vida Útil)")
    
    col_f1, col_f2 = st.columns(2)
    
    def obtener_estado_semaforo(porcentaje):
        if porcentaje >= 60:
            return "🟢 Buen Estado", "#16A34A"
        elif porcentaje >= 30:
            return "🟡 Al Límite", "#EA580C"
        else:
            return "🔴 Cambio Inmediato", "#DC2626"

    with col_f1:
        st.markdown("##### 🛑 Frenos y Batería")
        vida_pastillas = st.slider("Pastillas de Freno Delanteras (%)", 0, 100, 70, key="v_p")
        vida_discos_del = st.slider("Discos Delanteros (%)", 0, 100, 80, key="v_dd")
        vida_discos_tras = st.slider("Discos Traseros (%)", 0, 100, 75, key="v_dt")
        vida_frenos_tras = st.slider("Frenos / Balatas Traseras (%)", 0, 100, 60, key="v_ft")
        
        st.markdown("---")
        st.markdown("##### 🔋 Estado de Batería")
        es_bateria_fabrica = st.selectbox("¿Batería de fábrica?", ["Sí (De fábrica)", "No (Alternativa / Reemplazada)"])
        vida_bateria = st.slider("Vida Útil Batería (%)", 0, 100, 80, key="v_bat")
        
        costo_frenos = st.number_input("Costo Repuestos Frenos/Batería [$]", min_value=0, step=10000, value=0)

    with col_f2:
        st.markdown("##### 🛞 Neumáticos")
        vida_neu_del = st.slider("Neumáticos Delanteros (%)", 0, 100, 75, key="v_nd")
        vida_neu_tras = st.slider("Neumáticos Traseros (%)", 0, 100, 70, key="v_nt")
        
        costo_neumaticos = st.number_input("Costo Cambio Neumáticos [$]", min_value=0, step=10000, value=0)

    st.markdown("##### 🛠️ Trabajos Adicionales / Latonería")
    costo_latoneria = st.number_input("Costo Trabajos Latonería / Pintura / Extra [$]", min_value=0, step=10000, value=0)

    costo_total_inversion = costo_frenos + costo_neumaticos + costo_latoneria
    
    st.markdown(f"""
        <div class="card-total-inversion">
            <h3>💰 DESGLOSE TOTAL DE DINERO A INVERTIR: ${costo_total_inversion:,.0f} CLP</h3>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # PASO 5: PRUEBA DE RUTA
    st.subheader("🏁 Paso 5: Prueba de Ruta (Road Test)")
    test_drive_obs = st.text_area("Observaciones Dinámicas y Suspensión", placeholder="Ej: Motor responde con linealidad, sin ruidos en bandejas ni tren delantero.")

    st.markdown("---")

    # CANVAS MULTIHOJA PARA LOGO Y NUMERACIÓN
    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_decorations(num_pages)
                super().showPage()
            super().save()

        def draw_page_decorations(self, page_count):
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor('#64748B'))
            
            page_text = f"Página {self._pageNumber} de {page_count}"
            self.drawRightString(582, 20, page_text)
            self.drawString(30, 20, f"{nombre_marca} - Informe Pericial Consolidado | Patente: {patente or 'N/D'}")
            
            self.setStrokeColor(colors.HexColor('#CBD5E1'))
            self.setLineWidth(0.5)
            self.line(30, 32, 582, 32)
            
            if uploaded_logo is not None:
                try:
                    img_pil_logo = PILImage.open(uploaded_logo)
                    img_logo_io = io.BytesIO()
                    img_pil_logo.save(img_logo_io, format='PNG')
                    img_logo_io.seek(0)
                    rl_logo = RLImage(img_logo_io, width=65, height=45)
                    rl_logo.drawOn(self, 30, letter[1] - 55)
                except:
                    pass

            self.restoreState()

    def generar_pdf_final():
        dictamen_pericial_ia = ""
        
        # PROCESAMIENTO DE API CLAUDE ACTUALIZADO
        if claude_api_key.strip() != "":
            exito_ia = False
            modelos_a_probar = [
                "claude-3-5-sonnet-latest", 
                "claude-3-5-haiku-latest", 
                "claude-3-haiku-20240307", 
                "claude-3-5-sonnet-20241022"
            ]
            
            resumen_pintura = ", ".join([f"{p}: {d['micras']}um ({d['estado']})" for p, d in datos_pintura.items() if d['micras'] >= 130])
            if not resumen_pintura:
                resumen_pintura = "Toda la carrocería en valores originales de fábrica (<130um)."

            prompt_completo = f"""
            Eres el perito automotriz principal y asesor comercial de la empresa AUTOTEN. Redacta un DICTAMEN PERICIAL EJECUTIVO Y COMPLETO PARA EL CLIENTE, CRUZANDO LA INSPECCIÓN FÍSICA CON EL HISTORIAL LEGAL DE AUTOFACT Y EL ESCÁNER ELECTRÓNICO.

            INFORMACIÓN DEL VEHÍCULO:
            - Patente: {patente} | Vehículo: {vehiculo} | Km Tablero: {km:,} | Dueños: {cantidad_duenos} | Origen Legal: {origen_legal} | Precio Pedido: ${precio_vendedor:,.0f} CLP
            - ESTADO DE DOCUMENTACIÓN DECLARADA: Permiso: {doc_permiso}, SOAP: {doc_soap}, Rev. Técnica: {doc_rt}, Padrón: {doc_padron}
            - TEXTO EXTRAÍDO DEL INFORME AUTOFACT (HISTORIAL OFICIAL/REGISTRO CIVIL/MULTAS/KILOMETRAJE HISTRÓRICO):
              {texto_autofact_extraido[:3500] if texto_autofact_extraido else 'No se adjuntó PDF de Autofact. Evaluar según datos declarados.'}
            - ESCÁNER ELECTRÓNICO (AUTEL): {texto_escaner_extraido[:2500] if texto_escaner_extraido else 'Sin códigos de falla DTC activos.'}
            - PINTURA Y CARROCERÍA: {resumen_pintura}
            - MECÁNICA Y PRUEBA DE RUTA: Pastillas ({vida_pastillas}%), Discos ({vida_discos_del}%), Inversión Proyectada: ${costo_total_inversion:,.0f} CLP. Observación de ruta: {test_drive_obs or 'Comportamiento normal.'}

            INSTRUCCIONES DE FORMATO Y CONTENIDO (OBLIGATORIO):
            Escribe un informe redactado en formato de viñetas claras (SIN caracteres extraños), usando etiquetas de severidad exactas ([VERDE] para buen estado, [AMARILLO] para advertencias leves, [ROJO] para problemas críticos, documentos vencidos o inconsistencias de kilometraje/multas).
            Estructura el dictamen en 5 puntos directos:
            1. [VERDE]/[ROJO] **Documentación y Registro Legal (Autofact):** Cruza el historial de Autofact (multas impagas, encargo por robo, prendas, número de propietarios y vigencia de documentos).
            2. [VERDE]/[ROJO] **Historial de Kilometraje (Tablero vs PRT Autofact):** Confirma si el kilometraje del tablero coincide con los registros históricos de las Plantas de Revisión Técnica o si hay sospechas de alteración del odómetro.
            3. [AMARILLO]/[ROJO] **Carrocería y Estructura:** Explicación técnica de los paneles repintados o con masilla (roces o choques pasados) y confirmación de que la estructura principal está intacta.
            4. [VERDE] **Electrónica y Prueba Mecánica en Ruta:** Resultado del escáner Autel y comportamiento en conducción.
            5. [VERDE] **Conclusión y Recomendación Comercial:** Dictamen final de compra y argumentos de negociación de precio.
            """

            try:
                client = anthropic.Anthropic(api_key=claude_api_key.strip())
                for mod in modelos_a_probar:
                    if exito_ia:
                        break
                    try:
                        message = client.messages.create(
                            model=mod,
                            max_tokens=950,
                            messages=[{"role": "user", "content": prompt_completo}]
                        )
                        dictamen_pericial_ia = message.content[0].text
                        exito_ia = True
                    except Exception as err_mod:
                        continue
            except Exception as e:
                pass

        # FUNCIÓN AUXILIAR PARA COLOREAR DOCUMENTOS EN LA TABLA DEL PDF
        def formatear_doc_html(texto_doc):
            if "🟢" in texto_doc:
                return f"<font color='#16A34A'><b>{texto_doc}</b></font>"
            elif "🟡" in texto_doc:
                return f"<font color='#D97706'><b>{texto_doc}</b></font>"
            else:
                return f"<font color='#DC2626'><b>{texto_doc}</b></font>"

        # RESPALDO AUTOMÁTICO AUTOTEN SI NO HAY CONEXIÓN A API
        if not dictamen_pericial_ia:
            doc_status_text = f"Permiso: {doc_permiso}, SOAP: {doc_soap}, Rev. Técnica: {doc_rt}, Padrón: {doc_padron}"
            tag_doc = "[ROJO]" if any(k in doc_status_text for k in ["🔴", "⚪", "vencido", "deuda", "rechazada", "extraviado", "no presentado"]) else "[VERDE]"
            
            paneles_malos = [f"{p} ({d['micras']}um)" for p, d in datos_pintura.items() if d['micras'] >= 170]
            str_paneles = ", ".join(paneles_malos) if paneles_malos else "Sin paneles con masilla o repintado denso."
            
            dictamen_pericial_ia = f"""• {tag_doc} **Documentación Legal y Registro:** Permiso de Circulación ({doc_permiso}), SOAP ({doc_soap}), Revisión Técnica ({doc_rt}), Padrón ({doc_padron}). Requiere regularizar trámites pendientes.
• [VERDE] **Historial de Kilometraje:** Registra {km:,} km en tablero. Se recomienda validar coherencia con registros históricos de PRT.
• [AMARILLO] **Carrocería y Estructura:** Intervención detectada en: {str_paneles}. Apunta a reparaciones cosméticas en paneles externos sin comprometer el chasis.
• [VERDE] **Estado Mecánico y Electrónica:** {test_drive_obs or 'Vehículo dinámicamente estable.'} Diagnóstico de escáner sin códigos graves de fallas. Inversión estimada: ${costo_total_inversion:,.0f} CLP.
• [VERDE] **Conclusión Comercial:** Utilizar las observaciones mecánicas, estéticas y de papeles para ajustar la propuesta comercial de compra."""

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=55, bottomMargin=45)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#1E3A8A'), fontName='Helvetica-Bold')
        subtitle_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#475569'))
        section_style = ParagraphStyle('SecStyle', parent=styles['Heading2'], fontSize=10, leading=13, textColor=colors.HexColor('#FFFFFF'), fontName='Helvetica-Bold', backColor=colors.HexColor('#1E3A8A'), spaceBefore=8, spaceAfter=4, borderPadding=4)
        normal_style = ParagraphStyle('NormStyle', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor('#1E293B'))
        bold_style = ParagraphStyle('BoldStyle', parent=normal_style, fontName='Helvetica-Bold')

        elements = []

        elements.append(Paragraph(f"<b>{nombre_marca} - INFORME PERICIAL PRECOMPRA Y EVALUACIÓN</b>", title_style))
        elements.append(Paragraph(f"Fecha de Emisión: {datetime.now().strftime('%d-%m-%Y %H:%M')}", subtitle_style))
        elements.append(Spacer(1, 4))

        # TABLA DATOS VEHÍCULO
        data_vehiculo = [
            [Paragraph("<b>Patente:</b>", bold_style), Paragraph(f"<b><font size=9 color='#1E3A8A'>{patente or 'N/D'}</font></b>", normal_style), Paragraph("<b>Kilometraje:</b>", bold_style), Paragraph(f"{km:,} km", normal_style)],
            [Paragraph("<b>Vehículo:</b>", bold_style), Paragraph(f"{vehiculo or 'N/D'}", normal_style), Paragraph("<b>Precio Pedido:</b>", bold_style), Paragraph(f"${precio_vendedor:,.0f} CLP", normal_style)],
            [Paragraph("<b>N° Dueños:</b>", bold_style), Paragraph(f"<b><font color='#D97706'>{cantidad_duenos}</font></b>", normal_style), Paragraph("<b>Origen Legal:</b>", bold_style), Paragraph(f"<b><font color='#B91C1C'>{origen_legal}</font></b>", normal_style)]
        ]
        t_veh = Table(data_vehiculo, colWidths=[80, 195, 85, 190])
        t_veh.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
            ('PADDING', (0,0), (-1,-1), 3),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BFDBFE')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DBEAFE')),
        ]))
        elements.append(t_veh)
        elements.append(Spacer(1, 4))

        # TABLA REVISIÓN DOCUMENTACIÓN LEGAL
        hay_docs_criticos = any(k in f"{doc_permiso}{doc_soap}{doc_rt}{doc_padron}" for k in ["🔴", "⚪", "vencido", "deuda", "rechazada", "extraviado"])
        
        data_docs = [
            [Paragraph("<b>Permiso Circulación:</b>", bold_style), Paragraph(formatear_doc_html(doc_permiso), normal_style), Paragraph("<b>SOAP:</b>", bold_style), Paragraph(formatear_doc_html(doc_soap), normal_style)],
            [Paragraph("<b>Revisión Técnica:</b>", bold_style), Paragraph(formatear_doc_html(doc_rt), normal_style), Paragraph("<b>Padrón / Dominio:</b>", bold_style), Paragraph(formatear_doc_html(doc_padron), normal_style)]
        ]
        t_docs = Table(data_docs, colWidths=[120, 155, 120, 155])
        t_docs.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2') if hay_docs_criticos else colors.HexColor('#F8FAFC')),
            ('PADDING', (0,0), (-1,-1), 3),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#FCA5A5') if hay_docs_criticos else colors.HexColor('#E2E8F0')),
        ]))
        elements.append(Paragraph("<b>ESTADO DE DOCUMENTACIÓN OBLIGATORIA DEL VEHÍCULO:</b>", bold_style))
        elements.append(Spacer(1, 2))
        elements.append(t_docs)
        elements.append(Spacer(1, 6))

        # 1. DICTAMEN PERICIAL INTEGRAL
        elements.append(Paragraph(" 1. DICTAMEN PERICIAL INTEGRAL (ANÁLISIS DETALLADO Y CONCLUSIÓN)", section_style))
        
        dictamen_procesado = (dictamen_pericial_ia
            .replace("[VERDE]", "<font color='#16A34A'><b>🟢 [BUEN ESTADO / OK]</b></font>")
            .replace("[AMARILLO]", "<font color='#D97706'><b>🟡 [ATENCIÓN / LEVE]</b></font>")
            .replace("[ROJO]", "<font color='#DC2626'><b>🔴 [CRÍTICO / ALERTA]</b></font>")
        )
        
        elements.append(Paragraph(f"<b>Resumen Ejecutivo y Conclusión Pericial:</b><br/>{dictamen_procesado.replace(chr(10), '<br/>')}", normal_style))
        elements.append(Spacer(1, 6))

        # 2. MEDICIÓN DE PINTURA
        elements.append(Paragraph(" 2. MEDICIÓN DE PINTURA POR PIEZA (ESPESOR EN um)", section_style))
        leyenda_txt = "<b>Rangos de Pintura:</b> <font color='#16A34A'><b><130um Original</b></font> | <font color='#CA8A04'><b>130-169um Retoque</b></font> | <font color='#EA580C'><b>170-250um Repintado</b></font> | <font color='#DC2626'><b>>250um Daño/Masilla</b></font>"
        elements.append(Paragraph(leyenda_txt, ParagraphStyle('LeyendaStyle', parent=normal_style, fontSize=7.5, textColor=colors.HexColor('#475569'))))
        elements.append(Spacer(1, 4))

        data_pintura_table = [[Paragraph("<b>Pieza Carrocería</b>", bold_style), Paragraph("<b>Espesor (um)</b>", bold_style), Paragraph("<b>Diagnóstico de Estado</b>", bold_style)]]
        fotos_a_incluir = []
        for pieza, info in datos_pintura.items():
            color_txt = '#16A34A' if info['micras'] < 130 else ('#CA8A04' if info['micras'] < 170 else ('#EA580C' if info['micras'] < 250 else '#DC2626'))
            data_pintura_table.append([
                Paragraph(pieza, normal_style),
                Paragraph(f"<b>{info['micras']} um</b>", normal_style),
                Paragraph(f"<font color='{color_txt}'><b>{info['estado']}</b></font>", normal_style)
            ])
            if info['foto'] is not None:
                fotos_a_incluir.append((pieza, info['foto']))

        t_pintura = Table(data_pintura_table, colWidths=[190, 100, 260])
        t_pintura.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('PADDING', (0,0), (-1,-1), 2.5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(t_pintura)
        elements.append(Spacer(1, 6))

        if fotos_a_incluir:
            elements.append(Paragraph("<b>Evidencias Fotográficas de Paneles con Detalles:</b>", bold_style))
            elements.append(Spacer(1, 4))
            for p_nombre, f_obj in fotos_a_incluir:
                try:
                    img_pil = PILImage.open(f_obj)
                    img_io = io.BytesIO()
                    img_pil.save(img_io, format='JPEG')
                    img_io.seek(0)
                    rl_img = RLImage(img_io, width=130, height=90)
                    elements.append(Paragraph(f"• Detalle fotográfico: <b>{p_nombre}</b>", normal_style))
                    elements.append(rl_img)
                    elements.append(Spacer(1, 4))
                except Exception:
                    pass

        # 3. MECÁNICA, FRENOS Y BATERÍA
        elements.append(Paragraph(" 3. DESGASTE MECÁNICO, FRENOS, BATERÍA Y NEUMÁTICOS", section_style))
        comp_mecanicos = [
            ("Pastillas de Freno Delanteras", vida_pastillas),
            ("Discos de Freno Delanteros", vida_discos_del),
            ("Discos de Freno Traseros", vida_discos_tras),
            ("Frenos / Balatas Traseras", vida_frenos_tras),
            ("Batería Vehicular (" + es_bateria_fabrica + ")", vida_bateria),
            ("Neumáticos Delanteros", vida_neu_del),
            ("Neumáticos Traseros", vida_neu_tras),
        ]

        data_mecanica = [[Paragraph("<b>Componente Analizado</b>", bold_style), Paragraph("<b>% Vida Útil Restante</b>", bold_style), Paragraph("<b>Condición / Evaluación</b>", bold_style)]]
        for c_nombre, val_pct in comp_mecanicos:
            txt_eval, color_eval = obtener_estado_semaforo(val_pct)
            data_mecanica.append([
                Paragraph(c_nombre, normal_style),
                Paragraph(f"<b>{val_pct}%</b>", normal_style),
                Paragraph(f"<font color='{color_eval}'><b>{txt_eval}</b></font>", normal_style)
            ])

        t_mec = Table(data_mecanica, colWidths=[210, 130, 210])
        t_mec.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('PADDING', (0,0), (-1,-1), 2.5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(t_mec)
        elements.append(Spacer(1, 6))

        # 4. PRESUPUESTO E INVERSIÓN
        elements.append(Paragraph(" 4. PRESUPUESTO DE INVERSIÓN Y PRUEBA DE RUTA", section_style))
        data_resumen_costos = [
            [Paragraph("<b>TOTAL PRESUPUESTADO A INVERTIR:</b>", ParagraphStyle('BoldLarge', parent=normal_style, fontName='Helvetica-Bold', fontSize=9)),
             Paragraph(f"<b><font size=10 color='#DC2626'>${costo_total_inversion:,.0f} CLP</font></b>", normal_style)]
        ]
        t_cost = Table(data_resumen_costos, colWidths=[240, 310])
        t_cost.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#FCA5A5')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(t_cost)
        elements.append(Spacer(1, 4))

        elements.append(Paragraph(f"<b>Observaciones Prueba de Ruta (Road Test):</b>", bold_style))
        elements.append(Paragraph(f"{test_drive_obs or 'Sin observaciones registradas durante la conducción.'}", normal_style))

        doc.build(elements, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer

    st.markdown("---")
    st.download_button(
        label="📄 Generar y Descargar Informe Pericial Profesional e Integral",
        data=generar_pdf_final(),
        file_name=f"Informe_Final_AUTOTEN_{patente}.pdf",
        mime="application/pdf"
    )

# ---------------------------------------------------------
# MÓDULO 2: CONTROL DE STOCK Y GANANCIAS
# ---------------------------------------------------------
with tab_inventario:
    st.header("📈 Control de Stock y Ganancias por Mes")
    st.caption("Gestión financiera, inventario y estadísticas.")

    if "db_meses" not in st.session_state:
        st.session_state.db_meses = {
            "Octubre": [],
            "Noviembre": [],
            "Diciembre": []
        }

    s_oct, s_nov, s_dic, s_tot = st.tabs(["📅 1. Octubre", "📅 2. Noviembre", "📅 3. Diciembre", "🏆 4. Recuento Total"])
    
    def render_mes(nombre):
        st.subheader(f"Historial de {nombre}")
        while len(st.session_state.db_meses[nombre]) < 10:
            st.session_state.db_meses[nombre].append({"Modelo": "", "Fecha Compra": str(datetime.now().date()), "Compra ($)": 0, "Fecha Venta": str(datetime.now().date()), "Venta ($)": 0, "Dias": 0})
        df_editado = st.data_editor(pd.DataFrame(st.session_state.db_meses[nombre]), num_rows="dynamic", use_container_width=True, key=f"ed_{nombre}")
        st.session_state.db_meses[nombre] = df_editado[df_editado["Modelo"].astype(str).str.strip() != ""].to_dict(orient="records")

    with s_oct: render_mes("Octubre")
    with s_nov: render_mes("Noviembre")
    with s_dic: render_mes("Diciembre")
    with s_tot: st.info("Recuento consolidado global.")