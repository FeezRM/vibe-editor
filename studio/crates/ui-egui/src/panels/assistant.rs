//! Vibe Studio: the Assistant panel. Two views under one tab strip:
//!
//! - **Agent**: the user's Claude Code, running in the vibe-editor checkout with its skills and
//!   samples, and connected to this app. Its messages, the tools it runs, its permission prompts
//!   (Allow / Always / Deny) and its questions (option buttons) show here; the user answers and
//!   types the next message, as in a terminal session.
//! - **Activity**: every command that reached the app from the agent (or any other client of the
//!   control channel), newest first, with its result: what changed the timeline, and when.
//!
//! Automation ids: `assistant.tab.agent`, `assistant.tab.activity`, `assistant.input`,
//! `assistant.send`, `assistant.stop`, `assistant.new`, `assistant.mode.<mode>`,
//! `assistant.prompt.<n>.allow|always|deny`, `assistant.prompt.<n>.option.<q>.<i>`.

use egui::{Rect, RichText, Stroke, pos2, vec2};

use crate::FilmcraftApp;
use crate::assistant::{self, ChatLine};
use crate::theme::Tokens;

const BAR_H: f32 = 32.0;
const MODES: [(&str, &str, &str); 3] = [
    ("default", "Ask", "Ask before running commands or editing files (your project's permission settings apply)"),
    ("acceptEdits", "Auto-edit", "Edit files without asking; still ask before running other commands"),
    ("plan", "Plan", "Plan first: no changes until you approve the plan"),
];

pub fn show(app: &mut FilmcraftApp, ui: &mut egui::Ui, rect: Rect) {
    let t = app.tokens;
    let bar = Rect::from_min_size(rect.min, vec2(rect.width(), BAR_H));
    tab_bar(app, ui, bar);
    let body = Rect::from_min_max(pos2(rect.min.x, bar.max.y), rect.max);
    ui.painter().line_segment([bar.left_bottom(), bar.right_bottom()], Stroke::new(1.0, t.separator));
    if app.assistant.show_activity {
        activity(app, ui, body.shrink2(vec2(10.0, 6.0)));
    } else {
        agent(app, ui, body.shrink2(vec2(10.0, 8.0)));
    }
}

fn text_button(app: &mut FilmcraftApp, ui: &mut egui::Ui, r: Rect, id: &str, label: &str, tip: &str) -> bool {
    let t = app.tokens;
    let resp = ui.interact(r, egui::Id::unique(("assistant-btn", id)), egui::Sense::click()).on_hover_text(tip);
    app.auto.add(id, r, label);
    if resp.hovered() {
        ui.painter().rect_filled(r, 4.0, t.hover);
    }
    ui.painter().text(r.center(), egui::Align2::CENTER_CENTER, label, Tokens::ui(12.0), if resp.hovered() { t.text } else { t.text_dim });
    resp.clicked()
}

fn tab_bar(app: &mut FilmcraftApp, ui: &mut egui::Ui, bar: Rect) {
    let t = app.tokens;
    let p = ui.painter().clone();
    let mut x = bar.min.x + 12.0;
    let n = app.assistant.activity.len();
    let activity_label = if n == 0 { "Activity".to_string() } else { format!("Activity  {n}") };
    for (id, label, on) in [("agent", "Agent".to_string(), !app.assistant.show_activity), ("activity", activity_label, app.assistant.show_activity)] {
        let g = p.layout_no_wrap(label.clone(), Tokens::ui(13.0), t.text);
        let r = Rect::from_min_size(pos2(x - 4.0, bar.min.y), vec2(g.size().x + 8.0, bar.height()));
        let resp = ui.interact(r, egui::Id::unique(("assistant-tab", id)), egui::Sense::click());
        app.auto.add(&format!("assistant.tab.{id}"), r, &label);
        let col = if on || resp.hovered() { t.text } else { t.text_dim };
        p.galley_with_override_text_color(pos2(x, bar.center().y - g.size().y / 2.0), g.clone(), col);
        if on {
            p.line_segment([pos2(x, bar.max.y - 1.0), pos2(x + g.size().x, bar.max.y - 1.0)], Stroke::new(2.0, t.accent));
        }
        if resp.clicked() {
            app.assistant.show_activity = id == "activity";
        }
        x += g.size().x + 20.0;
    }
    let r = Rect::from_min_size(pos2(bar.max.x - 92.0, bar.min.y + 5.0), vec2(84.0, bar.height() - 10.0));
    if app.assistant.show_activity {
        if text_button(app, ui, r, "assistant.clearActivity", "Clear", "Clear the Activity list") {
            app.assistant.activity.clear();
        }
    } else if text_button(app, ui, r, "assistant.new", "New session", "End this agent session; the next message starts a new one") {
        app.assistant.new_session();
    }
    if app.assistant.busy() {
        let pulse = (ui.input(|i| i.time) * 3.0).sin() as f32 * 0.5 + 0.5;
        p.circle_filled(pos2(r.min.x - 10.0, bar.center().y), 3.5, t.accent.gamma_multiply(0.4 + 0.6 * pulse));
        ui.ctx().request_repaint();
    }
}

fn agent(app: &mut FilmcraftApp, ui: &mut egui::Ui, rect: Rect) {
    let composer_h = 112.0;
    let list = Rect::from_min_max(rect.min, pos2(rect.max.x, rect.max.y - composer_h));
    let composer = Rect::from_min_max(pos2(rect.min.x, rect.max.y - composer_h + 8.0), rect.max);
    let mut child = ui.new_child(egui::UiBuilder::new().max_rect(list));
    egui::ScrollArea::vertical().id_salt("assistant-chat").auto_shrink([false, false]).stick_to_bottom(true).show(&mut child, |ui| {
        ui.set_width(list.width() - 4.0);
        if app.assistant.lines.is_empty() {
            empty_state(app, ui);
        }
        for i in 0..app.assistant.lines.len() {
            line(app, ui, i);
        }
        if app.assistant.busy() {
            ui.add_space(4.0);
            let status =
                if app.assistant.status.is_empty() { "Working…".to_string() } else { format!("{}…", app.assistant.status.trim_end_matches('…')) };
            ui.label(RichText::new(status).font(Tokens::ui(12.0)).color(app.tokens.text_faint));
        }
    });
    composer_ui(app, ui, composer);
}

fn line(app: &mut FilmcraftApp, ui: &mut egui::Ui, i: usize) {
    let t = app.tokens;
    let Some(l) = app.assistant.lines.get(i).cloned() else { return };
    match l {
        ChatLine::User(s) => {
            ui.add_space(8.0);
            ui.label(RichText::new("You").font(Tokens::ui(11.0)).color(t.text_faint));
            ui.label(RichText::new(s).font(Tokens::ui(13.0)).color(t.text));
        }
        ChatLine::Agent(s) => {
            ui.add_space(6.0);
            ui.label(RichText::new(s).font(Tokens::ui(13.0)).color(t.text));
        }
        ChatLine::Tool { label, ok, .. } => {
            let (mark, col) = match ok {
                None => ("·", t.text_faint),
                Some(true) => ("✓", t.text_dim),
                Some(false) => ("✗", t.danger),
            };
            ui.label(RichText::new(format!("{mark} {label}")).font(Tokens::mono(11.0)).color(col));
        }
        ChatLine::Prompt(p) => prompt_card(app, ui, i, &p),
        ChatLine::Note(s) => {
            ui.label(RichText::new(s).font(Tokens::ui(11.0)).color(t.text_faint));
        }
        ChatLine::Error(s) => {
            ui.add_space(4.0);
            ui.label(RichText::new(s).font(Tokens::ui(12.0)).color(t.danger));
        }
    }
}

/// A permission prompt (Allow / Always / Deny) or a question (option buttons, then Answer).
fn prompt_card(app: &mut FilmcraftApp, ui: &mut egui::Ui, i: usize, p: &assistant::Prompt) {
    let t = app.tokens;
    ui.add_space(6.0);
    let frame = egui::Frame::new()
        .fill(t.field_bg)
        .stroke(Stroke::new(1.0, if p.answered.is_none() { t.accent } else { t.separator }))
        .corner_radius(egui::CornerRadius::same(4))
        .inner_margin(egui::Margin::same(8));
    frame.show(ui, |ui| {
        ui.set_width(ui.available_width());
        if p.is_question() {
            question(app, ui, i, p);
            return;
        }
        let title = if p.tool == "ExitPlanMode" { "Approve the plan?".to_string() } else { format!("Allow {}?", friendly_tool(&p.tool)) };
        ui.label(RichText::new(title).font(Tokens::semibold(12.0)).color(t.text));
        if let Some(plan) = p.input.get("plan").and_then(serde_json::Value::as_str) {
            ui.label(RichText::new(assistant::short(plan, 1_500)).font(Tokens::ui(12.0)).color(t.text_dim));
        } else {
            ui.label(RichText::new(&p.summary).font(Tokens::mono(11.0)).color(t.text_dim));
        }
        match p.answered {
            Some(allowed) => {
                ui.label(RichText::new(if allowed { "Allowed" } else { "Denied" }).font(Tokens::ui(11.0)).color(t.text_faint));
            }
            None => {
                ui.horizontal(|ui| {
                    let always = p.suggestions.as_array().is_some_and(|a| !a.is_empty());
                    let mut buttons = vec![("allow", if p.tool == "ExitPlanMode" { "Approve" } else { "Allow" }, true, false)];
                    if always {
                        buttons.push(("always", "Always allow", true, true));
                    }
                    buttons.push(("deny", if p.tool == "ExitPlanMode" { "Keep planning" } else { "Deny" }, false, false));
                    for (id, label, allow, always) in buttons {
                        let primary = id == "allow";
                        let b = egui::Button::new(RichText::new(label).color(if primary { t.on_accent } else { t.text })).fill(if primary {
                            t.accent
                        } else {
                            t.hover
                        });
                        let r = ui.add(b);
                        app.auto.add(&format!("assistant.prompt.{i}.{id}"), r.rect, label);
                        if r.clicked() {
                            app.assistant.answer(i, allow, always);
                        }
                    }
                });
            }
        }
    });
}

fn question(app: &mut FilmcraftApp, ui: &mut egui::Ui, i: usize, p: &assistant::Prompt) {
    let t = app.tokens;
    for (qi, q) in p.questions().iter().enumerate() {
        let text = q.get("question").and_then(serde_json::Value::as_str).unwrap_or("");
        ui.label(RichText::new(text).font(Tokens::semibold(12.0)).color(t.text));
        let picked = p.picks.get(qi).cloned().flatten();
        ui.horizontal_wrapped(|ui| {
            for (oi, o) in q.get("options").and_then(serde_json::Value::as_array).cloned().unwrap_or_default().iter().enumerate() {
                let label = o.get("label").and_then(serde_json::Value::as_str).unwrap_or("").to_string();
                let on = picked.as_deref() == Some(label.as_str());
                let b = egui::Button::new(RichText::new(&label).color(if on { t.on_accent } else { t.text })).fill(if on { t.accent } else { t.hover });
                let mut r = ui.add_enabled(p.answered.is_none(), b);
                if let Some(d) = o.get("description").and_then(serde_json::Value::as_str) {
                    r = r.on_hover_text(d);
                }
                app.auto.add(&format!("assistant.prompt.{i}.option.{qi}.{oi}"), r.rect, &label);
                if r.clicked()
                    && let Some(ChatLine::Prompt(pp)) = app.assistant.lines.get_mut(i)
                    && let Some(slot) = pp.picks.get_mut(qi)
                {
                    *slot = Some(label.clone());
                }
            }
        });
        ui.add_space(4.0);
    }
    match p.answered {
        Some(_) => {
            ui.label(RichText::new("Answered").font(Tokens::ui(11.0)).color(t.text_faint));
        }
        None => {
            ui.horizontal(|ui| {
                let ready = p.picks.iter().all(Option::is_some);
                let r = ui.add_enabled(ready, egui::Button::new(RichText::new("Answer").color(t.on_accent)).fill(t.accent));
                app.auto.add(&format!("assistant.prompt.{i}.allow"), r.rect, "Answer");
                if r.clicked() {
                    app.assistant.answer(i, true, false);
                }
                let r = ui.add(egui::Button::new(RichText::new("Skip").color(t.text)).fill(t.hover));
                app.auto.add(&format!("assistant.prompt.{i}.deny"), r.rect, "Skip");
                if r.clicked() {
                    app.assistant.answer(i, false, false);
                }
            });
        }
    }
}

fn composer_ui(app: &mut FilmcraftApp, ui: &mut egui::Ui, composer: Rect) {
    let t = app.tokens;
    let field = Rect::from_min_size(composer.min, vec2(composer.width(), composer.height() - 36.0));
    ui.painter().rect_filled(field, 4.0, t.field_bg);
    let id = egui::Id::unique("assistant-input");
    let focused = ui.memory(|m| m.has_focus(id));
    let mut send = false;
    if focused {
        // Enter sends; Shift+Enter makes a new line
        send = ui.input_mut(|i| i.consume_key(egui::Modifiers::NONE, egui::Key::Enter));
    }
    let mut fchild = ui.new_child(egui::UiBuilder::new().max_rect(field.shrink(6.0)));
    let hint =
        if app.assistant.running() { "Message the agent…" } else { "Ask the agent to edit this video, or anything you'd ask in a terminal session…" };
    let resp = fchild.add_sized(
        field.shrink(6.0).size(),
        egui::TextEdit::multiline(&mut app.assistant.input)
            .id(id)
            .frame(egui::Frame::NONE)
            .font(Tokens::ui(13.0))
            .text_color(t.text)
            .hint_text(RichText::new(hint).color(t.text_faint)),
    );
    app.auto.add_response("assistant.input", &resp, &app.assistant.input.clone());
    if resp.hovered() || resp.has_focus() {
        ui.painter().rect_stroke(field, 4.0, Stroke::new(1.0, if resp.has_focus() { t.accent } else { t.field_border }), egui::StrokeKind::Inside);
    }

    // mode chips on the left, Send / Stop on the right
    let row = Rect::from_min_max(pos2(composer.min.x, field.max.y + 6.0), pos2(composer.max.x, field.max.y + 32.0));
    let mode = if app.assistant.permission_mode.is_empty() { "default".to_string() } else { app.assistant.permission_mode.clone() };
    let mut x = row.min.x;
    for (key, label, tip) in MODES {
        let g = ui.painter().layout_no_wrap(label.to_string(), Tokens::ui(11.0), t.text);
        let r = Rect::from_min_size(pos2(x, row.min.y + 3.0), vec2(g.size().x + 14.0, 20.0));
        let on = mode == key;
        let resp = ui.interact(r, egui::Id::unique(("assistant-mode", key)), egui::Sense::click()).on_hover_text(tip);
        app.auto.add(&format!("assistant.mode.{key}"), r, label);
        if on {
            ui.painter().rect_filled(r, 4.0, t.pressed);
        } else if resp.hovered() {
            ui.painter().rect_filled(r, 4.0, t.hover);
        }
        ui.painter().text(r.center(), egui::Align2::CENTER_CENTER, label, Tokens::ui(11.0), if on { t.text } else { t.text_dim });
        if resp.clicked() && !on {
            app.assistant.set_permission_mode(key);
        }
        x = r.max.x + 4.0;
    }
    let btn = Rect::from_min_size(pos2(row.max.x - 72.0, row.min.y), vec2(72.0, 26.0));
    let busy = app.assistant.busy();
    let (label, auto_id) = if busy { ("Stop", "assistant.stop") } else { ("Send", "assistant.send") };
    let bresp = ui.interact(btn, egui::Id::unique("assistant-send"), egui::Sense::click());
    app.auto.add(auto_id, btn, label);
    let fill = if busy {
        t.hover
    } else if bresp.hovered() {
        t.accent_hover
    } else {
        t.accent
    };
    ui.painter().rect_filled(btn, 4.0, fill);
    ui.painter().text(btn.center(), egui::Align2::CENTER_CENTER, label, Tokens::ui(12.0), if busy { t.text } else { t.on_accent });
    if bresp.clicked() {
        if busy {
            app.assistant.interrupt();
        } else {
            send = true;
        }
    }
    if send && !busy {
        assistant::send(app);
        ui.memory_mut(|m| m.request_focus(id));
    }
}

fn empty_state(app: &mut FilmcraftApp, ui: &mut egui::Ui) {
    let t = app.tokens;
    ui.add_space(8.0);
    ui.label(RichText::new("Your Claude Code, inside the editor.").font(Tokens::ui(13.0)).color(t.text));
    ui.add_space(4.0);
    ui.label(
        RichText::new(
            "It runs in your vibe-editor folder with its skills, samples and CLAUDE.md, signed in as you are in the terminal, and it can see and change this timeline. Edit by hand any time; ask it for the rest.",
        )
        .font(Tokens::ui(12.0))
        .color(t.text_dim),
    );
    ui.add_space(8.0);
    for example in [
        "Edit projects/my-reel end to end and open the cut here.",
        "The punch-in at 0:08 is too much, make it subtle.",
        "Redo the graphic on \"it's called Muse\" with the real app icon.",
    ] {
        ui.label(RichText::new(format!("“{example}”")).font(Tokens::ui(12.0)).color(t.text_faint));
    }
    ui.add_space(8.0);
    let mut cont = app.assistant.continue_last;
    if ui.checkbox(&mut cont, RichText::new("Continue my last Claude Code session in this folder").font(Tokens::ui(11.0)).color(t.text_dim)).changed() {
        app.assistant.continue_last = cont;
    }
}

fn activity(app: &mut FilmcraftApp, ui: &mut egui::Ui, rect: Rect) {
    let t = app.tokens;
    let now = app.ui_clock;
    let mut child = ui.new_child(egui::UiBuilder::new().max_rect(rect));
    egui::ScrollArea::vertical().id_salt("assistant-activity").auto_shrink([false, false]).show(&mut child, |ui| {
        ui.set_width(rect.width() - 4.0);
        if app.assistant.activity.is_empty() {
            ui.add_space(8.0);
            ui.label(
                RichText::new("Nothing yet. Every change the agent makes to the timeline shows up here as it happens, newest first.")
                    .font(Tokens::ui(12.0))
                    .color(t.text_faint),
            );
        }
        for a in app.assistant.activity.iter().rev() {
            ui.add_space(4.0);
            ui.horizontal(|ui| {
                let (mark, col) = if a.ok { ("✓", t.text_dim) } else { ("✗", t.danger) };
                ui.label(RichText::new(mark).font(Tokens::mono(11.0)).color(col));
                ui.label(RichText::new(a.source.label()).font(Tokens::ui(11.0)).color(t.accent));
                ui.label(RichText::new(&a.command).font(Tokens::mono(12.0)).color(t.text));
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    ui.label(RichText::new(ago(now - a.at)).font(Tokens::ui(11.0)).color(t.text_faint));
                });
            });
            if !a.params.is_empty() && a.params != "{}" {
                ui.label(RichText::new(&a.params).font(Tokens::mono(11.0)).color(t.text_faint));
            }
            if !a.ok || !a.detail.is_empty() {
                ui.label(RichText::new(&a.detail).font(Tokens::ui(11.0)).color(if a.ok { t.text_faint } else { t.danger }));
            }
            let y = ui.cursor().min.y + 2.0;
            ui.painter().line_segment([pos2(rect.min.x, y), pos2(rect.max.x, y)], Stroke::new(1.0, t.separator));
            ui.add_space(4.0);
        }
    });
}

/// The tool's name as a person would say it: `mcp__vibe-studio__command_run` → "an editor command".
fn friendly_tool(tool: &str) -> String {
    match tool.strip_prefix("mcp__vibe-studio__") {
        Some("command_run") => "an editor command".into(),
        Some("command_batch") => "editor commands".into(),
        Some(t) => format!("the editor: {}", t.replace('_', " ")),
        None if tool.starts_with("mcp__") => tool.trim_start_matches("mcp__").replace("__", ": ").replace('_', " "),
        None => tool.to_string(),
    }
}

/// "now", "12 s", "3 min".
fn ago(seconds: f64) -> String {
    if !seconds.is_finite() || seconds < 5.0 {
        "now".into()
    } else if seconds < 60.0 {
        format!("{} s", seconds as u32)
    } else {
        format!("{} min", (seconds / 60.0) as u32)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use egui::Color32;

    #[test]
    fn text_on_the_brand_accent_is_dark_and_on_blue_is_white() {
        assert_eq!(crate::theme::on_accent(Color32::from_rgb(0xff, 0xc5, 0x31)), Color32::from_rgb(0x0b, 0x0b, 0x0c));
        assert_eq!(crate::theme::on_accent(Color32::from_rgb(0x2f, 0x6b, 0xdf)), Color32::WHITE);
    }

    #[test]
    fn ago_reads_naturally() {
        assert_eq!(ago(1.0), "now");
        assert_eq!(ago(12.4), "12 s");
        assert_eq!(ago(190.0), "3 min");
        assert_eq!(ago(f64::NAN), "now");
    }
}
