import numpy as np



def velocity_to_energy(velocity, mass, e_unit = "Joule", v_unit = "m/s"):
    """
    Convert velocity to kinectic energy
    Parameters

    ----------

    velocity
    mass
    e_unit == "Joule"
    v_unit == "m/s"


    """

    # Unit conversion factors
    v_conversion = {
        "m/s": 1,
        "km/s": 1e3,
        "cm/s": 1e-2,
        "mm/s": 1e-3
    }

    e_conversion = {
        "Joule": 1,
        "eV": 1.60218e-19,
        "keV": 1.60218e-16,
        "MeV": 1.60218e-13
    }

    if v_unit not in v_conversion:
        raise ValueError(f"Unsupported velocity unit: {v_unit}")

    if e_unit not in e_conversion:
        raise ValueError(f"Unsupported energy unit: {e_unit}")

    # Convert velocity to m/s
    velocity_m_s = velocity * v_conversion[v_unit]

    # Calculate kinetic energy in Joules
    energy_joule = 0.5 * mass * velocity_m_s**2

    # Convert energy to desired unit
    energy_converted = energy_joule / e_conversion[e_unit]

    return energy_converted


def time_of_flight(distance, time, mass, d_unit = "m", t_unit = "s"):
    """
    Calculate time of flight velocity
    Parameters

    ----------

    distance
    time
    d_unit == "m"
    t_unit == "s"


    """

    # Unit conversion factors
    d_conversion = {
        "m": 1,
        "km": 1e3,
        "cm": 1e-2,
        "mm": 1e-3
    }

    t_conversion = {
        "s": 1,
        "ms": 1e-3,
        "us": 1e-6,
        "ns": 1e-9
    }

    if d_unit not in d_conversion:
        raise ValueError(f"Unsupported distance unit: {d_unit}")

    if t_unit not in t_conversion:
        raise ValueError(f"Unsupported time unit: {t_unit}")

    # Convert distance to meters
    distance_m = distance * d_conversion[d_unit]

    # Convert time to seconds
    time_s = time * t_conversion[t_unit]

    # Calculate velocity in m/s
    velocity_m_s = distance_m / time_s

    energy_m_s = velocity_to_energy(velocity_m_s, mass=mass, e_unit="Joule", v_unit="m/s")

    return velocity_m_s, energy_m_s


def fractional_solid_angle(radius, distance, r_unit = "m", d_unit = "m"):
    """
    Calculate fractional solid angle
    Parameters

    ----------

    area
    distance
    r_unit == "m"
    d_unit == "m"


    """

    # Unit conversion factors


    d_conversion = {
        "m": 1,
        "cm": 1e-2,
        "mm": 1e-3,
        "ft": 0.3048
    }

    if r_unit not in d_conversion:
        raise ValueError(f"Unsupported area unit: {r_unit}")

    if d_unit not in d_conversion:
        raise ValueError(f"Unsupported distance unit: {d_unit}")

    # Convert area to m^2
    radius_m = radius * d_conversion[r_unit]

    # Convert distance to meters
    distance_m = distance * d_conversion[d_unit]

    # Calculate fractional solid angle
    solid_angle = 1/2 * (1 - distance_m / np.sqrt(distance_m**2 + radius_m**2))

    return solid_angle

