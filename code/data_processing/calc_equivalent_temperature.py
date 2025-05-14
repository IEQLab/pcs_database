def calculate_total_heat_transfer_coefficient(q_skin, t_skin, t_o):
    """Calculate total heat transfer coefficient [W/m²K]. from manikin outputs"""
    if t_skin == t_o:
        raise ValueError("t_skin and t_o cannot be the same to avoid division by zero.")
    return q_skin / (t_skin - t_o)

def calculate_equivalent_temperature(q_skin, t_skin, h_total):
    """Calculate equivalent temperature [°C] from heat flux, skin temp, and HTC."""
    if h_total == 0:
        raise ValueError("h_total must not be zero to avoid division by zero.")
    return t_skin - (q_skin / h_total)

def calculate_delta_total_heat_transfer_coefficient_by_pcs(h_total_with_pcs, h_total_without_pcs):
    """Calculate the difference introduced by PCS."""
    return h_total_with_pcs - h_total_without_pcs

def calculate_heat_transfer_by_pcs(q_skin_with_pcs, q_skin_without_pcs):
    """
    Evaluate heat transfer and change in heat transfer coefficient due to PCS.
    Returns:
        q_pcs: Heat transfer due to PCS [W/m²]
        delta_htc: Change in heat transfer coefficient [W/m²K]
    """
    return q_skin_with_pcs - q_skin_without_pcs

def main(q_skin_with_pcs, t_skin_with_pcs, t_o_with_pcs, q_skin_without_pcs, t_skin_without_pcs, t_o_without_pcs):
    h_total_with_pcs = calculate_total_heat_transfer_coefficient(q_skin_with_pcs, t_skin_with_pcs, t_o_with_pcs)
    h_total_without_pcs = calculate_total_heat_transfer_coefficient(q_skin_without_pcs, t_skin_without_pcs,
                                                                    t_o_without_pcs)

    q_pcs = calculate_heat_transfer_by_pcs(q_skin_with_pcs, q_skin_without_pcs)
    delta_h_total = calculate_delta_total_heat_transfer_coefficient_by_pcs(h_total_with_pcs, h_total_without_pcs)

    return q_pcs, delta_h_total


# Example usage:
if __name__ == "__main__":
    q_pcs, delta_h_total = main(60, 34, 25, 70, 34, 25)
    print(f"Heat transfer by PCS: {q_pcs}")
    print(f"Delta total heat transfer coefficient: {delta_h_total}")
