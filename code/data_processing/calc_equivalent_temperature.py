def calculate_h_total(q_skin, t_skin, t_o):
    if t_skin == t_o:
        raise ValueError("t_skin and t_o cannot be the same to avoid division by zero.")
    return q_skin / (t_skin - t_o)

def calculate_t_eq(q_skin, t_skin, h_total):
    if h_total == 0:
        raise ValueError("h_total must not be zero to avoid division by zero.")
    return t_skin - (q_skin / h_total)

def calculate_delta_h_total(h_total_with_pcs, h_total_without_pcs):
    return h_total_with_pcs - h_total_without_pcs

def calculate_delta_q_skin(q_skin_with_pcs, q_skin_without_pcs):
    return q_skin_with_pcs - q_skin_without_pcs

def calculate_delta_equivalent_temperature(q_skin_with_pcs, q_skin_without_pcs, h_total_without_pcs):
    delta_q = calculate_delta_q_skin(q_skin_with_pcs, q_skin_without_pcs)
    delta_t_eq = delta_q / h_total_without_pcs
    return delta_t_eq

def main(q_skin_with_pcs, t_skin_with_pcs, t_o_with_pcs, q_skin_without_pcs, t_skin_without_pcs, t_o_without_pcs):
    h_total_with_pcs = calculate_h_total(q_skin=q_skin_with_pcs, t_skin=t_skin_with_pcs, t_o=t_o_with_pcs)
    h_total_without_pcs = calculate_h_total(q_skin=q_skin_without_pcs, t_skin=t_skin_without_pcs, t_o=t_o_without_pcs)
    delta_h_total = calculate_delta_h_total(h_total_with_pcs=h_total_with_pcs, h_total_without_pcs=h_total_without_pcs)

    q_pcs = calculate_delta_q_skin(q_skin_with_pcs=q_skin_with_pcs, q_skin_without_pcs=q_skin_without_pcs)
    delta_t_eq = calculate_delta_equivalent_temperature(q_skin_with_pcs=q_skin_with_pcs, q_skin_without_pcs=q_skin_without_pcs, h_total_without_pcs=h_total_without_pcs)

    return q_pcs, delta_h_total, delta_t_eq


# Example usage:
if __name__ == "__main__":
    q_pcs, delta_h_total, delta_t_eq = main(
        q_skin_with_pcs=60, t_skin_with_pcs=34, t_o_with_pcs=25,
        q_skin_without_pcs=70, t_skin_without_pcs=34, t_o_without_pcs=25)
    print(f"Heat transfer by PCS: {q_pcs}")
    print(f"Delta total heat transfer coefficient: {delta_h_total}")
    print(f"Delta equivalent temperature: {delta_t_eq}")
