//! The app's wordmark: Vibe Studio draws its name as text in the UI font. (The editor this is built
//! on drew a third-party wordmark here; trademarks are not covered by the code licence.)

/// The name drawn as the wordmark.
pub const WORDMARK: &str = "Vibe Studio";

/// Draw the wordmark `height` points tall with its left edge at `left_center` (vertically
/// centred). Returns the drawn rect.
pub fn paint_wordmark(ui: &egui::Ui, left_center: egui::Pos2, height: f32, dark: bool) -> Option<egui::Rect> {
    let color = if dark { egui::Color32::from_rgb(0xe7, 0xe7, 0xea) } else { egui::Color32::from_rgb(0x13, 0x13, 0x15) };
    let galley = ui.painter().layout_no_wrap(WORDMARK.to_string(), crate::theme::Tokens::semibold(height), color);
    let r = egui::Rect::from_min_size(egui::pos2(left_center.x, left_center.y - galley.size().y / 2.0), galley.size());
    ui.painter().galley(r.min, galley, color);
    Some(r)
}
