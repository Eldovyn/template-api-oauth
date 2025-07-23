def kalkulator_emisi_default(sludge_ton, sludge_type):

    faktor_emisi = {"B3": 1300, "Non-B3": 1200}

    if sludge_type not in faktor_emisi:
        raise ValueError("Jenis sludge tidak valid. Masukkan 'B3' atau 'Non-B3'.")

    emisi_kg = sludge_ton * faktor_emisi[sludge_type]
    emisi_ton = round(emisi_kg / 1000, 2)
    return emisi_ton


def hitung_emisi_co2_coprocessing(M):

    fraksi_karbon = 0.30
    faktor_oksidasi = 1.0
    konversi_CO2 = 3.67
    konversi_kg = 1000

    emisi_kg = M * fraksi_karbon * faktor_oksidasi * konversi_CO2 * konversi_kg
    return round(emisi_kg, 2)


def hitung_emisi_co2e_kompos(M):

    massa_kg = M * 1000
    ef_ch4 = 4
    ef_n2o = 0.3
    gwp_ch4 = 28
    gwp_n2o = 265

    emisi_ch4 = massa_kg * ef_ch4 * gwp_ch4
    emisi_n2o = massa_kg * ef_n2o * gwp_n2o
    total_gram = emisi_ch4 + emisi_n2o
    emisi_kg = total_gram / 1000
    return round(emisi_kg, 2)


def hitung_emisi_maggot(massa_sludge):

    massa_sludge_kg = massa_sludge * 1000

    ef_ch4 = 0.5
    ef_n2o = 0.1
    gwp_ch4 = 28
    gwp_n2o = 265

    emisi_ch4 = massa_sludge_kg * ef_ch4 * gwp_ch4
    emisi_n2o = massa_sludge_kg * ef_n2o * gwp_n2o
    emisi_total_gram = emisi_ch4 + emisi_n2o
    emisi_total_kg = emisi_total_gram / 1000
    return round(emisi_total_kg, 2)
