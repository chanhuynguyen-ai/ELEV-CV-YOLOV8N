def _safe_visible(kpts, idx, conf=0.25):
    if idx >= len(kpts):
        return None
    p = kpts[idx]
    if len(p) < 3 or p[2] <= conf:
        return None
    return p


def classify_posture(kpts, bbox):
    if not kpts or len(kpts) < 17:
        return "unknown"

    x1, y1, x2, y2 = bbox
    w = max(1.0, x2 - x1)
    h = max(1.0, y2 - y1)

    visible = [p for p in kpts if len(p) >= 3 and p[2] > 0.25]
    if len(visible) < 5:
        return "unknown"

    ys = [p[1] for p in visible]
    torso_span = max(ys) - min(ys)
    aspect_ratio = w / h

    l_sh = _safe_visible(kpts, 5)
    r_sh = _safe_visible(kpts, 6)
    l_hp = _safe_visible(kpts, 11)
    r_hp = _safe_visible(kpts, 12)

    shoulder_y = None
    hip_y = None

    if l_sh and r_sh:
        shoulder_y = (l_sh[1] + r_sh[1]) / 2.0
    elif l_sh:
        shoulder_y = l_sh[1]
    elif r_sh:
        shoulder_y = r_sh[1]

    if l_hp and r_hp:
        hip_y = (l_hp[1] + r_hp[1]) / 2.0
    elif l_hp:
        hip_y = l_hp[1]
    elif r_hp:
        hip_y = r_hp[1]

    torso_height = None
    if shoulder_y is not None and hip_y is not None:
        torso_height = abs(hip_y - shoulder_y)

    # lying mạnh nếu bbox nằm ngang nhiều hoặc torso bị ép thấp rõ
    lying_votes = 0
    if aspect_ratio > 1.15:
        lying_votes += 1
    if torso_span < 0.42 * h:
        lying_votes += 1
    if torso_height is not None and torso_height < 0.22 * h:
        lying_votes += 1

    if lying_votes >= 2:
        return "lying"

    return "standing"


def is_fall_transition(prev_posture, curr_posture):
    return prev_posture == "standing" and curr_posture == "lying"



