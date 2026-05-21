import streamlit as st
import fitz
import io

from streamlit_sortables import sort_items

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="دمج ملفات PDF - IVR",
    layout="centered"
)

st.markdown("""
<style>

/* =========================
   FILE UPLOADER BOX
========================= */

[data-testid="stFileUploader"] {
    border: 2px dashed #999;
    border-radius: 18px;
    padding: 35px;
    background-color: rgba(255,255,255,0.02);
}

/* تكبير المنطقة الداخلية */

[data-testid="stFileUploaderDropzone"] {
    padding: 40px;
}

/* إخفاء النص الافتراضي */

[data-testid="stFileUploaderDropzone"] div div div span {
    display: none;
}

/* إضافة نص مخصص */

[data-testid="stFileUploaderDropzone"]::before {

    content: "📥 اسحب ملفات PDF إلى هنا أو اضغط للاختيار";

    display: flex;
    align-items: center;
    justify-content: center;

    width: 100%;
    height: 40px;

    font-size: 22px;
    font-weight: 600;

    color: #888;
}

/* تحسين الزر */

[data-testid="stBaseButton-secondary"] {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

st.title("دمج ملفات PDF")
st.caption("اسحب الملفات لتغيير ترتيبها ثم قم بالدمج")

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

                    pdf_doc.close()

                    break

            progress.progress(
                (index + 1) / total
            )

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

        st.success("تم الدمج بنجاح 🔥")

else:

    st.info("قم برفع ملفات PDF أولاً.")