import math

FCL_COEFFICIENT = 0.3

def calc_total_clothing_insulation(t_skin_clothed, t_o, q_total):
    It_m2K_per_W = (t_skin_clothed - t_o) / q_total
    return It_m2K_per_W / 0.155

def calc_nude_insulation(t_skin_nude, t_o, q_total):
    Ia_m2K_per_W = (t_skin_nude - t_o) / q_total
    return Ia_m2K_per_W / 0.155

def calc_intrinsic_clothing_insulation(t_skin_clothed, t_skin_nude, t_o_clothed, t_o_nude, q_total_clothed, q_total_nude):
    """
    Calculate intrinsic clothing insulation (Icl) using the exact quadratic solution
    derived from:
        fcl = 1 + 0.3 * Icl (there are several coefficients by different studies)
        Icl = It - Ia / fcl

    Substituting and simplifying gives:
        0.3 * Icl^2 + (1 - 0.3 * It) * Icl + (Ia - It) = 0

    This function solves the quadratic equation and returns the positive root Icl and fcl.

    Parameters:
    - t_skin_clothed: skin temperature with clothing [°C]
    - t_skin_nude: skin temperature without clothing [°C]
    - t_o: operative (ambient) temperature [°C]
    - q_total: sensible heat loss [W/m²]

    Returns:
    - Icl: intrinsic clothing insulation [clo]
    - fcl: clothing area factor (unitless)
    """
    It = calc_total_clothing_insulation(t_skin_clothed=t_skin_clothed, t_o=t_o_clothed, q_total=q_total_clothed)
    Ia = calc_nude_insulation(t_skin_nude=t_skin_nude, t_o=t_o_nude, q_total=q_total_nude)

    # Coefficients for the quadratic equation: a * Icl^2 + b * Icl + c = 0
    a = FCL_COEFFICIENT
    b = 1 - FCL_COEFFICIENT * It
    c = Ia - It

    discriminant = b**2 - 4 * a * c
    if discriminant < 0:
        raise ValueError("Negative discriminant — no real solution")

    Icl = (-b + math.sqrt(discriminant)) / (2 * a)  # only positive root
    fcl = 1 + FCL_COEFFICIENT * Icl

    return {
        "Icl": Icl,
        "fcl": fcl,
        "It": It,
        "Ia": Ia
    }
