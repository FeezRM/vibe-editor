//! Vibe Studio: the Assistant panel. Two views under one tab strip:
//!
//! - **Ask**: a conversation with Claude about the open edit. Claude reads the timeline, runs
//!   editor commands and looks at the frame (see [`crate::assistant`]); each command it runs shows
//!   as a line under its answer and is one undo step.
//! - **Activity**: every command Claude or an outside agent (Claude Code on the control channel or
//!   MCP bridge) ran, newest first, with its result, so what changed the edit is always visible.
//!
//! Automation ids: `assistant.tab.ask`, `assistant.tab.activity`, `assistant.input`,
//! `assistant.send`, `assistant.stop`, `assistant.clear`, `assistant.key`.

use egui::{Rect, RichText, Stroke, pos2, vec2};

use crate::FilmcraftApp;
use crate::assistant::{self, ChatLine, Source};
use crate::theme::Tokens;

const BAR_H: f32 = 32.0;

pub fn show(app: &mut FilmcraftApp, ui: &mut egui::Ui, rect: Rect) {
    let t = app.tokens;
    let bar = Rect::from_min_size(rect.min, vec2(rect.width(), BAR_H));
    tab_bar(app, ui, bar);
    let body = Rect::from_min_max(pos2(rect.min.x, bar.max.y), rect.max);
    ui.painter().line_segment([bar.left_bottom(), bar.right_bottom()], Stroke::new(1.0, t.separator));
    if app.assistant.show_activity {
        activity(app, ui, body.shrink2(vec2(10.0, 6.0)));
    } else {
        ask(app, ui, body.shrink2(vec2(10.0, 8.0)));
    }
}

fn tab_bar(app: &mut FilmcraftApp, ui: &mut egui::Ui, bar: Rect) {
    let t = app.tokens;
    let p = ui.painter().clone();
    let mut x = bar.min.x + 12.0;
    let n = app.assistant.activity.len();
    let activity_label = if n == 0 { "Activity".to_string() } else { format!("Activity  {n}") };
    for (id, label, on) in [("ask", "Ask".to_string(), !app.assistant.show_activity), ("activity", activity_label, app.assistant.show_activity)] {
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
    // busy indicator and Clear, on the right
    let clear = Rect::from_min_size(pos2(bar.max.x - 58.0, bar.min.y + 5.0), vec2(50.0, bar.height() - 10.0));
    let resp = ui.interact(clear, egui::Id::unique("assistant-clear"), egui::Sense::click()).on_hover_text("Forget this conversation");
    app.auto.add("assistant.clear", clear, "Clear");
    if resp.hovered() {
        p.rect_filled(clear, 4.0, t.hover);
    }
    p.text(clear.center(), egui::Align2::CENTER_CENTER, "Clear", Tokens::ui(12.0), if resp.hovered() { t.text } else { t.text_dim });
    if resp.clicked() {
        if app.assistant.show_activity {
            app.assistant.activity.clear();
        } else {
            app.assistant.clear();
        }
    }
    if app.assistant.busy() {
        let pulse = (ui.input(|i| i.time) * 3.0).sin() as f32 * 0.5 + 0.5;
        p.circle_filled(pos2(clear.min.x - 12.0, bar.center().y), 3.5, t.accent.gamma_multiply(0.4 + 0.6 * pulse));
        ui.ctx().request_repaint();
    }
}

fn ask(app: &mut FilmcraftApp, ui: &mut egui::Ui, rect: Rect) {
    let t = app.tokens;
    let composer_h = 104.0;
    let list = Rect::from_min_max(rect.min, pos2(rect.max.x, rect.max.y - composer_h));
    let composer = Rect::from_min_max(pos2(rect.min.x, rect.max.y - composer_h + 8.0), rect.max);

    let mut child = ui.new_child(egui::UiBuilder::new().max_rect(list));
    egui::ScrollArea::vertical().id_salt("assistant-chat").auto_shrink([false, false]).stick_to_bottom(true).show(&mut child, |ui| {
        ui.set_width(list.width() - 4.0);
        if app.assistant.lines.is_empty() {
            empty_state(app, ui);
        }
        for line in &app.assistant.lines {
            match line {
                ChatLine::User(s) => {
                    ui.add_space(6.0);
                    ui.label(RichText::new("You").font(Tokens::ui(11.0)).color(t.text_faint));
                    ui.label(RichText::new(s).font(Tokens::ui(13.0)).color(t.text));
                }
                ChatLine::Claude(s) => {
                    ui.add_space(6.0);
                    ui.label(RichText::new("Claude").font(Tokens::ui(11.0)).color(t.text_faint));
                    ui.label(RichText::new(s).font(Tokens::ui(13.0)).color(t.text));
                }
                ChatLine::Tool { label, ok } => {
                    let mark = if *ok { "✓" } else { "✗" };
                    let col = if *ok { t.text_dim } else { t.danger };
                    ui.label(RichText::new(format!("{mark} {label}")).font(Tokens::mono(11.0)).color(col));
                }
                ChatLine::Note(s) => {
                    ui.label(RichText::new(s).font(Tokens::ui(12.0)).color(t.text_faint));
                }
                ChatLine::Error(s) => {
                    ui.add_space(4.0);
                    ui.label(RichText::new(s).font(Tokens::ui(12.0)).color(t.danger));
                }
            }
        }
        if app.assistant.busy() {
            ui.add_space(4.0);
            ui.label(RichText::new("Working…").font(Tokens::ui(12.0)).color(t.text_faint));
        }
    });

    // composer: the field, then a hint and Send / Stop
    let field = Rect::from_min_size(composer.min, vec2(composer.width(), composer.height() - 34.0));
    ui.painter().rect_filled(field, 4.0, t.field_bg);
    let id = egui::Id::unique("assistant-input");
    let focused = ui.memory(|m| m.has_focus(id));
    let mut send = false;
    if focused {
        // Enter sends; Shift+Enter makes a new line
        send = ui.input_mut(|i| i.consume_key(egui::Modifiers::NONE, egui::Key::Enter));
    }
    let mut fchild = ui.new_child(egui::UiBuilder::new().max_rect(field.shrink(6.0)));
    let resp = fchild.add_sized(
        field.shrink(6.0).size(),
        egui::TextEdit::multiline(&mut app.assistant.input)
            .id(id)
            .frame(egui::Frame::NONE)
            .font(Tokens::ui(13.0))
            .text_color(t.text)
            .hint_text(RichText::new("Ask about this edit, or ask for a change…").color(t.text_faint)),
    );
    app.auto.add("assistant.input", resp.rect, &app.assistant.input.clone());
    if resp.hovered() || resp.has_focus() {
        ui.painter().rect_stroke(field, 4.0, Stroke::new(1.0, if resp.has_focus() { t.accent } else { t.field_border }), egui::StrokeKind::Inside);
    }

    let row_y = field.max.y + 6.0;
    ui.painter().text(
        pos2(composer.min.x, row_y + 12.0),
        egui::Align2::LEFT_CENTER,
        "Enter to send · Shift+Enter for a new line",
        Tokens::ui(11.0),
        t.text_faint,
    );
    let btn = Rect::from_min_size(pos2(composer.max.x - 72.0, row_y), vec2(72.0, 26.0));
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
            app.assistant.stop();
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
    ui.label(RichText::new("Ask Claude about this edit, or ask it to make a change.").font(Tokens::ui(13.0)).color(t.text));
    ui.add_space(4.0);
    for example in ["Tighten the pauses on V1 to under 0.1 s.", "Add a 110 % punch-in at 8.1 s.", "Why does the caption at 0:05 feel late?"] {
        ui.label(RichText::new(format!("“{example}”")).font(Tokens::ui(12.0)).color(t.text_dim));
    }
    ui.add_space(10.0);
    ui.label(
        RichText::new(format!(
            "Claude ({}) works through the same commands as the menus, and every change is one undo step. It uses ANTHROPIC_API_KEY from the environment, or a key pasted here (kept in memory only):",
            assistant::MODEL
        ))
        .font(Tokens::ui(11.0))
        .color(t.text_faint),
    );
    ui.add_space(2.0);
    let resp = ui.add(egui::TextEdit::singleline(&mut app.assistant.key).password(true).hint_text("sk-ant-…").desired_width(f32::INFINITY));
    app.auto.add("assistant.key", resp.rect, "API key");
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
                RichText::new("Nothing yet. Commands Claude runs here, or that an agent sends over the control channel (Claude Code running the pipeline), show up as they happen.")
                    .font(Tokens::ui(12.0))
                    .color(t.text_faint),
            );
        }
        for a in app.assistant.activity.iter().rev() {
            ui.add_space(4.0);
            ui.horizontal(|ui| {
                let (mark, col) = if a.ok { ("✓", t.text_dim) } else { ("✗", t.danger) };
                ui.label(RichText::new(mark).font(Tokens::mono(11.0)).color(col));
                let chip = match a.source {
                    Source::Claude => t.accent,
                    Source::Agent => t.text_dim,
                };
                ui.label(RichText::new(a.source.label()).font(Tokens::ui(11.0)).color(chip));
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
