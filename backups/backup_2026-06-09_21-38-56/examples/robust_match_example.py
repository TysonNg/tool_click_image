from core.vision import capture_screen_gray, find_best_match
from scenario.io import load_templates_from_file


def main():
    scenario_path = r"scenarios\maple\Daily Dungeon\Daily Dungeon.json"
    _scenario, templates, _metadata = load_templates_from_file(scenario_path, prompt_for_missing=False)

    image_steps = [tpl for tpl in templates if tpl["type"] == "image"]
    if not image_steps:
        print("No image templates found.")
        return

    step = image_steps[0]
    screen_gray = capture_screen_gray()
    match = find_best_match(
        screen_gray,
        step.get("imgs") or [step["img"]],
        threshold=step.get("threshold", 0.8),
        template_names=step.get("paths") or [step["path"]],
        masks=step.get("masks") or [step.get("mask")],
    )

    print("Found:", match.found)
    print("Position:", (match.center_x, match.center_y))
    print("Score:", round(match.score, 4))
    print("Scale:", match.scale)
    print("Template:", match.template_name)
    print("Method:", match.method)


if __name__ == "__main__":
    main()
