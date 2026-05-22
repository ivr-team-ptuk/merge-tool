import streamlit as st
import fitz
import io

from streamlit_sortables import sort_items

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="دمج ملفات PDF - IVR",
    layout="wide"
)

# =========================
# LOAD CSS
# =========================

with open("styles/style.css", encoding="utf-8") as f:

    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# =========================
# TITLE
# =========================

st.title("دمج ملفات PDF")
st.caption(
    "اسحب الملفات لتغيير ترتيبها ثم قم بالدمج"
)

# =========================
# LAYOUT
# =========================

# ROW 1 - NAVBAR
st.markdown("""
<div class="ivr-navbar">
    <a href="https://ivr-home.streamlit.app" target="_blank">Home</a>
    <a href="https://ivr-merge-tool.streamlit.app" target="_blank">Merge PDF</a>
    <a href="https://ivr-watermark-tool.streamlit.app" target="_blank">Watermark PDF</a>
    <a href="https://ivr-imagetopdf-tool.streamlit.app" target="_blank">Image to PDF</a>
</div>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

st.title("")
st.title("دمج ملفات PDF")
st.caption(
    "اسحب الملفات لتغيير ترتيبها ثم قم بالدمج"
)

controls_col, preview_col = st.columns(
    [1, 1.1]
)

# =========================
# LEFT SIDE
# =========================

with controls_col:

    # =========================
    # FILE UPLOAD
    # =========================

    uploaded_pdfs = st.file_uploader(
        "اسحب ملفات PDF هنا أو اضغط للاختيار",
        type=["pdf"],
        accept_multiple_files=True,
        help="يمكنك رفع عدة ملفات دفعة واحدة"
    )

    # =========================
    # MAIN
    # =========================

    if uploaded_pdfs:

        st.subheader("ترتيب الملفات")

        # =========================
        # FILE NAMES
        # =========================

        file_names = [
            file.name
            for file in uploaded_pdfs
        ]

        # =========================
        # DRAG & DROP SORT
        # =========================

        sorted_names = sort_items(
            file_names,
            direction="vertical"
        )

        st.divider()

        # =========================
        # BOOKMARK OPTION
        # =========================

        add_bookmarks = st.checkbox(
            "إضافة علامات مرجعية",
            value=True
        )

        bookmark_titles = {}

        if add_bookmarks:

            st.subheader(
                "أسماء العلامات المرجعية"
            )

            for file_name in sorted_names:

                clean_name = file_name.replace(
                    ".pdf",
                    ""
                )

                bookmark_titles[file_name] = st.text_input(
                    f"علامة: {file_name}",
                    value=clean_name
                )

        # =========================
        # OUTPUT FILE NAME
        # =========================

        output_name = st.text_input(
            "اسم الملف النهائي",
            value="merged_file"
        )

        # =========================
        # MERGE BUTTON
        # =========================

        if st.button("دمج وتحميل"):

            merged_doc = fitz.open()

            progress = st.progress(0)

            total = len(sorted_names)

            # =========================
            # TOC
            # =========================

            toc = []

            current_page = 1

            # =========================
            # MERGE FILES
            # =========================

            for index, selected_name in enumerate(sorted_names):

                for uploaded_file in uploaded_pdfs:

                    if uploaded_file.name == selected_name:

                        pdf_bytes = uploaded_file.getvalue()

                        pdf_doc = fitz.open(
                            stream=pdf_bytes,
                            filetype="pdf"
                        )

                        merged_doc.insert_pdf(pdf_doc)

                        # =========================
                        # BOOKMARK
                        # =========================

                        if add_bookmarks:

                            bookmark_title = bookmark_titles[
                                selected_name
                            ]

                            toc.append([
                                1,
                                bookmark_title,
                                current_page
                            ])

                        current_page += len(pdf_doc)

                        pdf_doc.close()

                        break

                progress.progress(
                    (index + 1) / total
                )

            # =========================
            # SET TOC
            # =========================

            if add_bookmarks and toc:

                merged_doc.set_toc(toc)

            # =========================
            # SAVE OUTPUT
            # =========================

            output_buffer = io.BytesIO()

            merged_doc.save(output_buffer)

            output_buffer.seek(0)

            merged_doc.close()

            # =========================
            # DOWNLOAD BUTTON
            # =========================

            st.download_button(
                label="تحميل الملف المدمج",
                data=output_buffer,
                file_name=f"{output_name}.pdf",
                mime="application/pdf"
            )

            st.success(
                "تم الدمج بنجاح 🔥"
            )

    else:

        st.info(
            "قم برفع ملفات PDF أولاً."
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

# =========================
# RIGHT SIDE
# =========================

with preview_col:

    st.subheader("المعاينة")

    if uploaded_pdfs:

        try:

            preview_file = uploaded_pdfs[0]

            preview_doc = fitz.open(
                stream=preview_file.getvalue(),
                filetype="pdf"
            )

            total_pages = len(preview_doc)

            col1, col2 = st.columns([3,1])

            with col1:

                preview_page_number = st.slider(
                    "التنقل السريع",
                    1,
                    total_pages,
                    1
                )

            with col2:

                preview_page_number = st.number_input(
                    "الصفحة",
                    min_value=1,
                    max_value=total_pages,
                    value=preview_page_number,
                    step=1
                )

            preview_page = preview_doc[
                preview_page_number - 1
            ]

            pix = preview_page.get_pixmap(
                matrix=fitz.Matrix(1.5, 1.5)
            )

            image_bytes = pix.tobytes("png")

            st.image(
                image_bytes,
                use_container_width=True
            )

            preview_doc.close()

        except Exception as e:

            st.error(
                f"خطأ في المعاينة: {e}"
            )

    else:

        st.info(
            "قم برفع ملف لرؤية المعاينة."
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )