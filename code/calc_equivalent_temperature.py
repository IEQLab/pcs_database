def calculate_total_heat_transfer_coefficient(q_skin, t_skin, t_o):
    if t_skin == t_o:
        raise ValueError("t_skin and t_o cannot be the same to avoid division by zero.")
    return q_skin / (t_skin - t_o)


def calculate_delta_total_heat_transfer_coefficient_by_pcs(h_total_with_pcs, h_total_without_pcs):
    return h_total_with_pcs - h_total_without_pcs

def calculate_heat_transfer_by_pcs(q_skin_with_pcs, q_skin_without_pcs):
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
